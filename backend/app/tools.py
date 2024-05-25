import os
from enum import Enum
from functools import lru_cache
from typing import Optional, Annotated

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.retriever import create_retriever_tool
from langchain_community.agent_toolkits.connery import ConneryToolkit
from langchain_community.retrievers.kay import KayAiRetriever
from langchain_community.retrievers.pubmed import PubMedRetriever
from langchain_community.retrievers.wikipedia import WikipediaRetriever
from langchain_community.retrievers.you import YouRetriever
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.tools.connery import ConneryService
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import (
    TavilyAnswer as _TavilyAnswer,
)
from langchain_community.tools.tavily_search import (
    TavilySearchResults,
)
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.tools import Tool
from langchain_robocorp import ActionServerToolkit
from typing_extensions import TypedDict

from app.upload import vstore

from langchain_core.tools import tool
from datetime import datetime
from app.datastat_wrap import *
from app.meeting_tool import *
from app.email_tool import reminder_reveiw_code
from app.pull_tool import *
from app.issue_tool import *
import structlog
from langchain_community.document_loaders import WebBaseLoader

logger = structlog.get_logger(__name__)

class DDGInput(BaseModel):
    query: str = Field(description="search query to look up")


class ArxivInput(BaseModel):
    query: str = Field(description="search query to look up")


class PythonREPLInput(BaseModel):
    query: str = Field(description="python command to run")


class DallEInput(BaseModel):
    query: str = Field(description="image description to generate image from")


class AvailableTools(str, Enum):
    ACTION_SERVER = "action_server_by_sema4ai"
    CONNERY = "ai_action_runner_by_connery"
    DDG_SEARCH = "ddg_search"
    TAVILY = "search_tavily"
    TAVILY_ANSWER = "search_tavily_answer"
    RETRIEVAL = "retrieval"
    ARXIV = "arxiv"
    YOU_SEARCH = "you_search"
    SEC_FILINGS = "sec_filings_kai_ai"
    PRESS_RELEASES = "press_releases_kai_ai"
    PUBMED = "pubmed"
    WIKIPEDIA = "wikipedia"
    DALL_E = "dall_e"
    NOW_TIME_TOOL = "now_time_tool"
    DATA_STAT_ALL_SIG = "data_state_all_sig"
    DATA_STAT_SIG_DETAIL = "data_state_sig_detail"
    DATA_STAT_CONTRIBUTE = "data_state_contribute"
    MEET_GROUP = "meet_group"
    MEET_INFO = "meet_info"
    CREATE_MEET = "meet_create"
    SEND_EMAIL = "send_email"
    PULL_AUTHOER = "pull_auther"
    PULL_DETAIL = "pull_detail"
    PUBLIC_RETRIEVAL = "public_retrieval"
    ISSUE_LABEL = "issue_label"
    ISSUE_DETAIL = "issue_detail"
    WEB_LOADER = "web_loader"


class ToolConfig(TypedDict):
    ...


class BaseTool(BaseModel):
    type: AvailableTools
    name: Optional[str]
    description: Optional[str]
    config: Optional[ToolConfig]
    multi_use: Optional[bool] = False


class ActionServerConfig(ToolConfig):
    url: str
    api_key: str


class ActionServer(BaseTool):
    type: AvailableTools = Field(AvailableTools.ACTION_SERVER, const=True)
    name: str = Field("Action Server by Sema4.ai", const=True)
    description: str = Field(
        (
            "Run AI actions with "
            "[Sema4.ai Action Server](https://github.com/Sema4AI/actions)."
        ),
        const=True,
    )
    config: ActionServerConfig
    multi_use: bool = Field(True, const=True)


class Connery(BaseTool):
    type: AvailableTools = Field(AvailableTools.CONNERY, const=True)
    name: str = Field("AI Action Runner by Connery", const=True)
    description: str = Field(
        (
            "Connect OpenGPTs to the real world with "
            "[Connery](https://github.com/connery-io/connery)."
        ),
        const=True,
    )


class DDGSearch(BaseTool):
    type: AvailableTools = Field(AvailableTools.DDG_SEARCH, const=True)
    name: str = Field("DuckDuckGo Search", const=True)
    description: str = Field(
        "Search the web with [DuckDuckGo](https://pypi.org/project/duckduckgo-search/).",
        const=True,
    )


class Arxiv(BaseTool):
    type: AvailableTools = Field(AvailableTools.ARXIV, const=True)
    name: str = Field("Arxiv", const=True)
    description: str = Field("Searches [Arxiv](https://arxiv.org/).", const=True)


class YouSearch(BaseTool):
    type: AvailableTools = Field(AvailableTools.YOU_SEARCH, const=True)
    name: str = Field("You.com Search", const=True)
    description: str = Field(
        "Uses [You.com](https://you.com/) search, optimized responses for LLMs.",
        const=True,
    )


class SecFilings(BaseTool):
    type: AvailableTools = Field(AvailableTools.SEC_FILINGS, const=True)
    name: str = Field("SEC Filings (Kay.ai)", const=True)
    description: str = Field(
        "Searches through SEC filings using [Kay.ai](https://www.kay.ai/).", const=True
    )


class PressReleases(BaseTool):
    type: AvailableTools = Field(AvailableTools.PRESS_RELEASES, const=True)
    name: str = Field("Press Releases (Kay.ai)", const=True)
    description: str = Field(
        "Searches through press releases using [Kay.ai](https://www.kay.ai/).",
        const=True,
    )


class PubMed(BaseTool):
    type: AvailableTools = Field(AvailableTools.PUBMED, const=True)
    name: str = Field("PubMed", const=True)
    description: str = Field(
        "Searches [PubMed](https://pubmed.ncbi.nlm.nih.gov/).", const=True
    )


class Wikipedia(BaseTool):
    type: AvailableTools = Field(AvailableTools.WIKIPEDIA, const=True)
    name: str = Field("Wikipedia", const=True)
    description: str = Field(
        ("Constrains: 回答内容必须限定在openEuler和openGauss社区的领域问题，避免涉及不相关的娱乐、政治或文化内容。"\
        "Searches [Wikipedia](https://pypi.org/project/wikipedia/)."),
        const=True
    )


class Tavily(BaseTool):
    type: AvailableTools = Field(AvailableTools.TAVILY, const=True)
    name: str = Field("Search (Tavily)", const=True)
    description: str = Field(
        (
            "Constrains: 回答内容必须限定在openEuler和openGauss社区的领域问题，避免涉及不相关的娱乐、政治或文化内容。"
            "Uses the [Tavily](https://app.tavily.com/) search engine. "
            "Includes sources in the response."
        ),
        const=True,
    )


class TavilyAnswer(BaseTool):
    type: AvailableTools = Field(AvailableTools.TAVILY_ANSWER, const=True)
    name: str = Field("Search (short answer, Tavily)", const=True)
    description: str = Field(
        (
            "Uses the [Tavily](https://app.tavily.com/) search engine. "
            "This returns only the answer, no supporting evidence."
        ),
        const=True,
    )


class Retrieval(BaseTool):
    type: AvailableTools = Field(AvailableTools.RETRIEVAL, const=True)
    name: str = Field("Retrieval", const=True)
    description: str = Field("Look up information in uploaded files.", const=True)

class PublicRetrieval(BaseTool):
    type: AvailableTools = Field(AvailableTools.PUBLIC_RETRIEVAL, const=True)
    name: str = Field("PublicRetrieval", const=True)
    description: str = Field("Look up information in public uploaded files", const=True)

class DallE(BaseTool):
    type: AvailableTools = Field(AvailableTools.DALL_E, const=True)
    name: str = Field("Generate Image (Dall-E)", const=True)
    description: str = Field(
        "Generates images from a text description using OpenAI's DALL-E model.",
        const=True,
    )

class NowTime(BaseTool):
    type: AvailableTools = Field(AvailableTools.NOW_TIME_TOOL, const=True)
    name: str = Field("get now time", const=True)
    description: str = Field(
        "获取服务器的本地时间.",
        const=True,
    )

class DataStateAllSig(BaseTool):
    type: AvailableTools = Field(AvailableTools.DATA_STAT_ALL_SIG, const=True)
    name: str = Field("get datastat all sig", const=True)
    description: str = Field(
        "社区服务运营数据集，可以查询所有的sig组.",
        const=True,
    )
class DataStateSigDetail(BaseTool):
    type: AvailableTools = Field(AvailableTools.DATA_STAT_SIG_DETAIL, const=True)
    name: str = Field("get datastat sig detail", const=True)
    description: str = Field(
        "社区服务运营数据集，可以查询sig组详情，包括miantainer、committer等信息.",
        const=True,
    )
class DataStateContribute(BaseTool):
    type: AvailableTools = Field(AvailableTools.DATA_STAT_CONTRIBUTE, const=True)
    name: str = Field("get datastat contribute", const=True)
    description: str = Field(
        "社区服务运营数据集，可以查询按 pr/issue/coment 维度的贡献值.",
        const=True,
    )
class MeetGroup(BaseTool):
    type: AvailableTools = Field(AvailableTools.MEET_GROUP, const=True)
    name: str = Field("get all meeting sig group", const=True)
    description: str = Field(
        "获取会议系统的所有sig信息.",
        const=True,
    )
class MeetInfo(BaseTool):
    type: AvailableTools = Field(AvailableTools.MEET_INFO, const=True)
    name: str = Field("get a sig meeting detail info", const=True)
    description: str = Field(
        "获取某个sig的会议预定详情.",
        const=True,
    )
class MeetCreating(BaseTool):
    type: AvailableTools = Field(AvailableTools.CREATE_MEET, const=True)
    name: str = Field("create a meeting", const=True)
    description: str = Field(
        "通过输入信息在会议系统创建一个会议",
        const=True,
    )
class SendEmail(BaseTool):
    type: AvailableTools = Field(AvailableTools.SEND_EMAIL, const=True)
    name: str = Field("send a email", const=True)
    description: str = Field(
        "通过email催促并通知committer或maintainer进行代码检视",
        const=True,
    )
class PullAuthor(BaseTool):
    type: AvailableTools = Field(AvailableTools.PULL_AUTHOER, const=True)
    name: str = Field("get pull by author keyword", const=True)
    description: str = Field(
        "模糊搜索pull提交的人名",
        const=True,
    )
class PullDetail(BaseTool):
    type: AvailableTools = Field(AvailableTools.PULL_DETAIL, const=True)
    name: str = Field("get pull detail info", const=True)
    description: str = Field(
        "获取PR的详情",
        const=True,
    )

class IssueLabel(BaseTool):
    type: AvailableTools = Field(AvailableTools.ISSUE_LABEL, const=True)
    name: str = Field("get issue  all label", const=True)
    description: str = Field(
        "issue标签列表",
        const=True,
    )

class IssueDetail(BaseTool):
    type: AvailableTools = Field(AvailableTools.ISSUE_DETAIL, const=True)
    name: str = Field("get issue detail info", const=True)
    description: str = Field(
        "获取issue列表详情",
        const=True,
    )

class WebLoader(BaseTool):
    type: AvailableTools = Field(AvailableTools.WEB_LOADER, const=True)
    name: str = Field("get web loader by url", const=True)
    description: str = Field(
        "爬取指定URL的内容，获取openGauss的社区贡献指南非常有用",
        const=True,
    )

RETRIEVAL_DESCRIPTION = """Can be used to look up information that was uploaded to this assistant.
If the user is referencing particular files, that is often a good hint that information may be here.
If the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!"""

PUBLIC_RETRIEVAL_DES = """"
- Role: openGauss社区贡献者和维护者信息检索专家
- Background: 用户需要了解openGauss开源社区中特定项目的committer和maintainer信息。
- Profile: 作为openGauss社区的资深成员，您对社区的贡献者和维护者信息有深入的了解。
- Skills: 社区知识、信息检索、数据库管理、成员角色识别。
- Goals: 提供openGauss社区中特定项目的committer和maintainer的详细信息。
- Constrains: 确保提供的信息最新、最准确，并且遵守社区的隐私政策和信息披露规则，社区领域知识优先检索，未检索到的再调用其他工具
- OutputFormat: 结合检索到的社区贡献者和维护者信息，生成详细的列表或描述。
- Workflow:
  1. 接收并分析用户关于特定项目committer和maintainer的查询请求。
  2. 在社区数据库和文档中检索相关的贡献者和维护者信息。
  3. 根据检索结果，生成包含姓名、贡献类型、活跃度等信息的详细列表。
- Examples:
  用户问题：Infra SIG 组的 Maintainer 是谁？
  生成回答：根据查询结果，Infra SIG 组的 Maintainer 是钟君（@zhongjun2，jun.zhongjun2@gmail.com）。如果您有其他问题或需要进一步的信息，请随时告诉我！
- Initialization: 欢迎咨询openGauss社区贡献者和维护者信息。请提供您想要查询的项目或版本，我将为您提供详细的信息。
"""


def get_retriever(assistant_id: str, thread_id: str):
    return vstore.as_retriever(
        search_kwargs={"filter": {"namespace": {"$in": [assistant_id, thread_id]}}}
    )

@lru_cache(maxsize=5)
def get_retrieval_tool(assistant_id: str, thread_id: str, description: str):
    return create_retriever_tool(
        get_retriever(assistant_id, thread_id),
        "Retriever",
        description,
    )

@lru_cache(maxsize=1)
def _get_duck_duck_go():
    return DuckDuckGoSearchRun(args_schema=DDGInput)


@lru_cache(maxsize=1)
def _get_arxiv():
    return ArxivQueryRun(api_wrapper=ArxivAPIWrapper(), args_schema=ArxivInput)


@lru_cache(maxsize=1)
def _get_you_search():
    return create_retriever_tool(
        YouRetriever(n_hits=3, n_snippets_per_hit=3),
        "you_search",
        "Searches for documents using You.com",
    )


@lru_cache(maxsize=1)
def _get_sec_filings():
    return create_retriever_tool(
        KayAiRetriever.create(
            dataset_id="company", data_types=["10-K", "10-Q"], num_contexts=3
        ),
        "sec_filings_search",
        "Search for a query among SEC Filings",
    )


@lru_cache(maxsize=1)
def _get_press_releases():
    return create_retriever_tool(
        KayAiRetriever.create(
            dataset_id="company", data_types=["PressRelease"], num_contexts=6
        ),
        "press_release_search",
        "Search for a query among press releases from US companies",
    )


@lru_cache(maxsize=1)
def _get_pubmed():
    return create_retriever_tool(
        PubMedRetriever(), "pub_med_search", "Search for a query on PubMed"
    )


@lru_cache(maxsize=1)
def _get_wikipedia():
    return create_retriever_tool(
        WikipediaRetriever(), "wikipedia", "Search for a query on Wikipedia"
    )


@lru_cache(maxsize=1)
def _get_tavily():
    tavily_search = TavilySearchAPIWrapper()
    return TavilySearchResults(api_wrapper=tavily_search, name="search_tavily")


@lru_cache(maxsize=1)
def _get_tavily_answer():
    tavily_search = TavilySearchAPIWrapper()
    return _TavilyAnswer(api_wrapper=tavily_search, name="search_tavily_answer")


def _get_action_server(**kwargs: ActionServerConfig):
    toolkit = ActionServerToolkit(url=kwargs["url"], api_key=kwargs["api_key"])
    tools = toolkit.get_tools()
    return tools


@lru_cache(maxsize=1)
def _get_connery_actions():
    connery_service = ConneryService()
    connery_toolkit = ConneryToolkit.create_instance(connery_service)
    tools = connery_toolkit.get_tools()
    return tools


@lru_cache(maxsize=1)
def _get_dalle_tools():
    return Tool(
        "Dall-E-Image-Generator",
        DallEAPIWrapper(size="1024x1024", quality="hd").run,
        "A wrapper around OpenAI DALL-E API. Useful for when you need to generate images from a text description. Input should be an image description.",
    )

@tool
def now_time_tool(
    input: Annotated[str, "可以不用参数"] = ''
):
    """当您需要获取当前时间非常有效
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _get_now_time():
    return now_time_tool

@tool
def web_loader(url: str) -> str:
    """
    抓取url对应网页的内容, openGauss贡献指导的URL为: https://opengauss.org/zh/contribution/detail.html
    - 重要提示：获取贡献指南时，输出结果添加一句\"openGauss getting Started 更详细指南请参见: https://opengauss.org/zh/contribution\"
    """
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs[0].page_content

@lru_cache(maxsize=1)
def _get_web_loader():
    return web_loader

@lru_cache(maxsize=1)
def _get_datastat_sig_all():
    logger.info("get_datastat_tools{} {}".format(os.getenv('DATASTAT_BASE_URL'), os.getenv('COMMUNITY')))
    return query_community_all_sigs

@lru_cache(maxsize=1)
def _get_datastat_contribute():
    return query_community_usercontribute

@lru_cache(maxsize=3)
def _get_datastat_sig_detail():
    if os.getenv('COMMUNITY') != "opengauss":
        return query_community_detail_info
    else:
        return read_readme_content

@lru_cache(maxsize=1)
def _get_meet_group():
    return get_all_meeting_group

@lru_cache(maxsize=1)
def _get_meet_info():
    return get_meetinfo_by_group

@lru_cache(maxsize=1)
def _create_a_meet():
    return create_a_meeting

@lru_cache(maxsize=1)
def _send_a_email():
    return reminder_reveiw_code

@lru_cache(maxsize=3)
def _get_pull_author():
    return get_pulls_authors

@lru_cache(maxsize=1)
def _get_pull_detail():
    return get_pulls_detail_info

@lru_cache(maxsize=3)
def _get_issue_label():
    return get_issues_labels

@lru_cache(maxsize=1)
def _get_issue_detail():
    return get_issues_detail_info

TOOLS = {
    AvailableTools.ACTION_SERVER: _get_action_server,
    AvailableTools.CONNERY: _get_connery_actions,
    AvailableTools.DDG_SEARCH: _get_duck_duck_go,
    AvailableTools.ARXIV: _get_arxiv,
    AvailableTools.YOU_SEARCH: _get_you_search,
    AvailableTools.SEC_FILINGS: _get_sec_filings,
    AvailableTools.PRESS_RELEASES: _get_press_releases,
    AvailableTools.PUBMED: _get_pubmed,
    AvailableTools.TAVILY: _get_tavily,
    AvailableTools.WIKIPEDIA: _get_wikipedia,
    AvailableTools.TAVILY_ANSWER: _get_tavily_answer,
    AvailableTools.DALL_E: _get_dalle_tools,
    AvailableTools.NOW_TIME_TOOL: _get_now_time,
    AvailableTools.DATA_STAT_ALL_SIG: _get_datastat_sig_all,
    AvailableTools.DATA_STAT_SIG_DETAIL: _get_datastat_sig_detail,
    AvailableTools.DATA_STAT_CONTRIBUTE: _get_datastat_contribute,
    AvailableTools.MEET_GROUP: _get_meet_group,
    AvailableTools.MEET_INFO: _get_meet_info,
    AvailableTools.CREATE_MEET: _create_a_meet,
    AvailableTools.SEND_EMAIL: _send_a_email,
    AvailableTools.PULL_AUTHOER: _get_pull_author,
    AvailableTools.PULL_DETAIL: _get_pull_detail,
    AvailableTools.PUBLIC_RETRIEVAL: get_retrieval_tool,
    AvailableTools.ISSUE_LABEL: _get_issue_label,
    AvailableTools.ISSUE_DETAIL: _get_issue_detail,
    AvailableTools.WEB_LOADER: _get_web_loader,
}
