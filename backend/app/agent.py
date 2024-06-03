import pickle
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence, Union

from langchain_core.messages import AnyMessage
from langchain_core.runnables import (
    ConfigurableField,
    RunnableBinding,
)
from langgraph.graph.message import Messages
from langgraph.pregel import Pregel

from langchain_core.tracers.schemas import Run

from app.agent_types.tools_agent import get_tools_agent_executor
from app.agent_types.xml_agent import get_xml_agent_executor
from app.chatbot import get_chatbot_executor
from app.llms import (
    get_anthropic_llm,
    get_google_llm,
    get_mixtral_fireworks,
    get_ollama_llm,
    get_openai_llm,
)
from app.retrieval import get_retrieval_executor
from psycopg_pool import AsyncConnectionPool
from app.checkpoint import (
    PostgresCheckpoint, PickleCheckpointSerializer
)
import os
from app.tools import (
    RETRIEVAL_DESCRIPTION,
    TOOLS,
    AvailableTools,
    Retrieval,
    Tavily,
    TavilyAnswer,
    Wikipedia,
    get_retrieval_tool,
    PUBLIC_RETRIEVAL_DES,
    get_retriever,
    NowTime,
    DataStateAllSig,
    DataStateSigDetail,
    DataStateContribute,
    MeetGroup,
    MeetInfo,
    MeetCreating,
    SendEmail,
    PullAuthor,
    PullDetail,
    PullLabel,
    PullRepo,
    PullBranch,
    PullSig,
    PublicRetrieval,
    IssueLabel,
    IssueDetail,
    IssueAssign,
    WebLoader,
)

Tool = Union[
    Wikipedia,
    Tavily,
    TavilyAnswer,
    Retrieval,
    NowTime,
    DataStateAllSig,
    DataStateSigDetail,
    DataStateContribute,
    MeetGroup,
    MeetInfo,
    MeetCreating,
    SendEmail,
    PullAuthor,
    PullDetail,
    PullLabel,
    PullRepo,
    PullBranch,
    PullSig,
    PublicRetrieval,
    IssueLabel,
    IssueDetail,
    IssueAssign,
    WebLoader,
]

class AgentType(str, Enum):
    GPT_35_TURBO = "GPT 3.5 Turbo"
    GPT_4 = "GPT 4 Turbo"
    GPT_4O = "GPT 4o"
    AZURE_OPENAI = "GPT 4 (Azure OpenAI)"
    CLAUDE2 = "Claude 2"
    BEDROCK_CLAUDE2 = "Claude 2 (Amazon Bedrock)"
    GEMINI = "GEMINI"
    OLLAMA = "Ollama"


DEFAULT_SYSTEM_MESSAGE = """
- Role: 开源社区专家
- Background: 用户需要一个智能助手来帮助解答有关openGauss社区的领域问题，如PR（Pull Request）、issue、会议和开源流程等。
- Profile: 你是一个专注于开源社区管理的专家，拥有丰富的知识储备和经验，能够准确回答社区成员的问题。
- Skills: 熟悉openGauss社区的运作方式、开源流程、项目管理工具和社区文化。
- Goals: 提供准确、专业且及时的领域内问题解答，帮助社区成员更好地参与和贡献。
- Constrains: 回答内容必须限定在openGauss社区的领域问题，避免涉及不相关的娱乐、政治或文化内容。
- OutputFormat: 清晰、简洁的文本回答，必要时提供链接或进一步的资源推荐。
- Workflow:
1. 确认用户的问题属于openGauss社区的领域问题。
2. 提供准确且专业的解答，包括相关的开源流程、工具使用和最佳实践。
3. 如果需要，提供进一步的资源链接或推荐。
- Examples:
问题：如何在openGauss社区提交一个PR？
回答：要提交一个Pull Request（PR）到openGauss社区，首先需要在社区的代码仓库中找到你想要贡献的项目，然后按照以下步骤操作：
- Fork项目到你的个人账户。
- Clone你的Fork到本地。
- 创建一个新的分支并进行你的更改。
- 提交更改并推送到你的Fork。
- 通过你的Fork向原仓库提交PR。
- Initialization: 欢迎使用社区智能助手，我是你的开源社区专家。如果你有任何关于openGauss社区的问题，请随时提问，我会尽力为你提供帮助。
"""

async_pool = AsyncConnectionPool(
    # Example configuration
    conninfo="postgresql://{}:{}@{}:{}/{}".format(os.environ["POSTGRES_USER"],
        os.environ["POSTGRES_PASSWORD"], os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_PORT"], os.environ["POSTGRES_DB"]),
    max_size=20,
)

CHECKPOINTER = PostgresCheckpoint(
    serial=PickleCheckpointSerializer(),
    async_conn=async_pool,
)


def get_agent_executor(
    tools: list,
    agent: AgentType,
    system_message: str,
    interrupt_before_action: bool,
):
    if agent == AgentType.GPT_35_TURBO:
        llm = get_openai_llm()
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action, CHECKPOINTER
        )
    elif agent == AgentType.GPT_4:
        llm = get_openai_llm(model="gpt-4-turbo")
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action, CHECKPOINTER
        )
    elif agent == AgentType.GPT_4O:
        llm = get_openai_llm(model="gpt-4o")
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action, CHECKPOINTER
        )
    elif agent == AgentType.AZURE_OPENAI:
        llm = get_openai_llm(azure=True)
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action, CHECKPOINTER
        )
    elif agent == AgentType.CLAUDE2:
        llm = get_anthropic_llm()
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action, CHECKPOINTER
        )
    elif agent == AgentType.BEDROCK_CLAUDE2:
        llm = get_anthropic_llm(bedrock=True)
        return get_xml_agent_executor(
            tools, llm, system_message, interrupt_before_action, CHECKPOINTER
        )
    elif agent == AgentType.GEMINI:
        llm = get_google_llm()
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action, CHECKPOINTER
        )
    elif agent == AgentType.OLLAMA:
        llm = get_ollama_llm()
        return get_tools_agent_executor(
            tools, llm, system_message, interrupt_before_action, CHECKPOINTER
        )

    else:
        raise ValueError("Unexpected agent type")


class ConfigurableAgent(RunnableBinding):
    tools: Sequence[Tool]
    agent: AgentType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    retrieval_description: str = RETRIEVAL_DESCRIPTION
    interrupt_before_action: bool = False
    assistant_id: Optional[str] = None
    thread_id: Optional[str] = None
    user_id: Optional[str] = None

    def __init__(
        self,
        *,
        tools: Sequence[Tool],
        agent: AgentType = AgentType.GPT_35_TURBO,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        assistant_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        retrieval_description: str = RETRIEVAL_DESCRIPTION,
        interrupt_before_action: bool = False,
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        **others: Any,
    ) -> None:
        others.pop("bound", None)
        _tools = []
        for _tool in tools:
            if _tool["type"] == AvailableTools.RETRIEVAL:
                if assistant_id is None or thread_id is None:
                    raise ValueError(
                        "Both assistant_id and thread_id must be provided if Retrieval tool is used"
                    )
                _tools.append(
                    get_retrieval_tool(assistant_id, thread_id, retrieval_description)
                )
            elif _tool["type"] == AvailableTools.PUBLIC_RETRIEVAL:
                _tools.append(
                    get_retrieval_tool("public", "public", PUBLIC_RETRIEVAL_DES)
                )
            else:
                tool_config = _tool.get("config", {})
                _returned_tools = TOOLS[_tool["type"]](**tool_config)
                if isinstance(_returned_tools, list):
                    _tools.extend(_returned_tools)
                else:
                    _tools.append(_returned_tools)
        _agent = get_agent_executor(
            _tools, agent, system_message, interrupt_before_action
        )
        agent_executor = _agent.with_config({"recursion_limit": 50})
        super().__init__(
            tools=tools,
            agent=agent,
            system_message=system_message,
            retrieval_description=retrieval_description,
            bound=agent_executor,
            kwargs=kwargs or {},
            config=config or {},
        )


class LLMType(str, Enum):
    GPT_35_TURBO = "GPT 3.5 Turbo"
    GPT_4 = "GPT 4 Turbo"
    GPT_4O = "GPT 4o"
    AZURE_OPENAI = "GPT 4 (Azure OpenAI)"
    CLAUDE2 = "Claude 2"
    BEDROCK_CLAUDE2 = "Claude 2 (Amazon Bedrock)"
    GEMINI = "GEMINI"
    MIXTRAL = "Mixtral"
    OLLAMA = "Ollama"


def get_chatbot(
    llm_type: LLMType,
    system_message: str,
):
    if llm_type == LLMType.GPT_35_TURBO:
        llm = get_openai_llm()
    elif llm_type == LLMType.GPT_4:
        llm = get_openai_llm(gpt_4=True)
    elif llm_type == LLMType.AZURE_OPENAI:
        llm = get_openai_llm(azure=True)
    elif llm_type == LLMType.CLAUDE2:
        llm = get_anthropic_llm()
    elif llm_type == LLMType.BEDROCK_CLAUDE2:
        llm = get_anthropic_llm(bedrock=True)
    elif llm_type == LLMType.GEMINI:
        llm = get_google_llm()
    elif llm_type == LLMType.MIXTRAL:
        llm = get_mixtral_fireworks()
    elif llm_type == LLMType.OLLAMA:
        llm = get_ollama_llm()
    else:
        raise ValueError("Unexpected llm type")
    return get_chatbot_executor(llm, system_message, CHECKPOINTER)


class ConfigurableChatBot(RunnableBinding):
    llm: LLMType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    user_id: Optional[str] = None

    def __init__(
        self,
        *,
        llm: LLMType = LLMType.GPT_35_TURBO,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        **others: Any,
    ) -> None:
        others.pop("bound", None)

        chatbot = get_chatbot(llm, system_message)
        super().__init__(
            llm=llm,
            system_message=system_message,
            bound=chatbot,
            kwargs=kwargs or {},
            config=config or {},
        )


chatbot = (
    ConfigurableChatBot(llm=LLMType.GPT_35_TURBO, checkpoint=CHECKPOINTER)
    .configurable_fields(
        llm=ConfigurableField(id="llm_type", name="LLM Type"),
        system_message=ConfigurableField(id="system_message", name="Instructions"),
    )
    .with_types(
        input_type=Messages,
        output_type=Sequence[AnyMessage],
    )
)


class ConfigurableRetrieval(RunnableBinding):
    llm_type: LLMType
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    assistant_id: Optional[str] = None
    thread_id: Optional[str] = None
    user_id: Optional[str] = None

    def __init__(
        self,
        *,
        llm_type: LLMType = LLMType.GPT_35_TURBO,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        assistant_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        config: Optional[Mapping[str, Any]] = None,
        **others: Any,
    ) -> None:
        others.pop("bound", None)
        retriever = get_retriever(assistant_id, thread_id)
        if llm_type == LLMType.GPT_35_TURBO:
            llm = get_openai_llm()
        elif llm_type == LLMType.GPT_4:
            llm = get_openai_llm(model="gpt-4-turbo")
        elif llm_type == LLMType.GPT_4O:
            llm = get_openai_llm(model="gpt-4o")
        elif llm_type == LLMType.AZURE_OPENAI:
            llm = get_openai_llm(azure=True)
        elif llm_type == LLMType.CLAUDE2:
            llm = get_anthropic_llm()
        elif llm_type == LLMType.BEDROCK_CLAUDE2:
            llm = get_anthropic_llm(bedrock=True)
        elif llm_type == LLMType.GEMINI:
            llm = get_google_llm()
        elif llm_type == LLMType.MIXTRAL:
            llm = get_mixtral_fireworks()
        elif llm_type == LLMType.OLLAMA:
            llm = get_ollama_llm()
        else:
            raise ValueError("Unexpected llm type")
        chatbot = get_retrieval_executor(llm, retriever, system_message, CHECKPOINTER)
        super().__init__(
            llm_type=llm_type,
            system_message=system_message,
            bound=chatbot,
            kwargs=kwargs or {},
            config=config or {},
        )


chat_retrieval = (
    ConfigurableRetrieval(llm_type=LLMType.GPT_35_TURBO, checkpoint=CHECKPOINTER)
    .configurable_fields(
        llm_type=ConfigurableField(id="llm_type", name="LLM Type"),
        system_message=ConfigurableField(id="system_message", name="Instructions"),
        assistant_id=ConfigurableField(
            id="assistant_id", name="Assistant ID", is_shared=True
        ),
        thread_id=ConfigurableField(id="thread_id", name="Thread ID", is_shared=True),
    )
    .with_types(
        input_type=Dict[str, Any],
        output_type=Dict[str, Any],
    )
)

def fn_end(run_obj : Run):
    print("run exec time", run_obj.end_time - run_obj.start_time)

agent: Pregel = (
    ConfigurableAgent(
        agent=AgentType.GPT_35_TURBO,
        tools=[],
        system_message=DEFAULT_SYSTEM_MESSAGE,
        retrieval_description=RETRIEVAL_DESCRIPTION,
        assistant_id=None,
        thread_id=None,
    )
    .configurable_fields(
        agent=ConfigurableField(id="agent_type", name="Agent Type"),
        system_message=ConfigurableField(id="system_message", name="Instructions"),
        interrupt_before_action=ConfigurableField(
            id="interrupt_before_action",
            name="Tool Confirmation",
            description="If Yes, you'll be prompted to continue before each tool is executed.\nIf No, tools will be executed automatically by the agent.",
        ),
        assistant_id=ConfigurableField(
            id="assistant_id", name="Assistant ID", is_shared=True
        ),
        thread_id=ConfigurableField(id="thread_id", name="Thread ID", is_shared=True),
        tools=ConfigurableField(id="tools", name="Tools"),
        retrieval_description=ConfigurableField(
            id="retrieval_description", name="Retrieval Description"
        ),
    )
    .configurable_alternatives(
        ConfigurableField(id="type", name="Bot Type"),
        default_key="agent",
        prefix_keys=True,
        chatbot=chatbot,
        chat_retrieval=chat_retrieval,
    )
    .with_types(
        input_type=Messages,
        output_type=Sequence[AnyMessage],
    )
    .with_listeners(
        on_end=fn_end,
    )
)

if __name__ == "__main__":
    import asyncio

    from langchain.schema.messages import HumanMessage

    async def run():
        async for m in agent.astream_events(
            HumanMessage(content="whats your name"),
            config={"configurable": {"user_id": "2", "thread_id": "test1"}},
            version="v1",
        ):
            print(m)

    asyncio.run(run())
