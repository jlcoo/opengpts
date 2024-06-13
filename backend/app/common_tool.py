from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chains import OpenAIModerationChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI
from datetime import datetime
from typing import Annotated
from langchain_community.tools.tavily_search import (
    TavilyAnswer as _TavilyAnswer,
)
from langchain_community.tools.tavily_search import (
    TavilySearchResults,
)
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.retrievers.wikipedia import WikipediaRetriever
from langchain.tools.retriever import create_retriever_tool

@tool
def now_time_tool(
    input: Annotated[str, "可以不用参数"] = ''
):
    """当您需要获取当前时间非常有效
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def web_loader(url: str) -> str:
    """
    抓取url对应网页的内容, openGauss贡献指导的URL为: https://opengauss.org/zh/contribution/detail.html
    - 重要提示：获取贡献指南时，输出结果添加一句\"openGauss getting Started 更详细指南请参见: https://opengauss.org/zh/contribution\"
    CLA签署指导的URL:https://clasign.osinfra.cn/sign/gitee_opengauss-1614047760000855378
    """
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs[0].page_content

@tool
def recommend_questions(scenes: Annotated[str, "输入推荐问题场景，比如 PR 相关问题"]) -> str:
    """当出现场景问答时候，调用当前这个recommend_questions tool,当您需要获取场景问答时，非常有用，会返回推荐问题,
    比如 场景问答：会议查询以及预定
        场景问答：SIG信息
        场景问答：社区贡献
        场景问答：PR详情、PR Review
        场景问答：社区数据 ,保留该tool输出格式
    """
    # 社区贡献
    # 社区数据
    # PR相关
    pr_scenes = "<div class=\"chat-question-content\">" \
                "<div class=\"chat-question-desc\">关于 PR信息 你可以问我任何问题,也可以尝试点击以下问题开始：</div>" \
                "<div class=\"chat-question-list\">" \
                "<div class=\"chat-question-list-item\">获取QA SIG组的PR信息</div>" \
                "<div class=\"chat-question-list-item\">获取QA SIG组下的issue详情</div>" \
                "<div class=\"chat-question-list-item\">查询我的gitee name,并查询我最近在Infra SIG组提交的PR有哪些，其中有几个是处于open状态</div>" \
                "<div class=\"chat-question-list-item\">查询我的gitee name,并查询我在Infra " \
                "SIG组最近一次提交的PR，并找到该PR对应SIG的maintainer，发邮件催促maintainer检视该PR</div>" \
                "</div>" \
                "</div>"
    # Issue相关
    # SIG信息
    sig_scene = "<div class=\"chat-question-content\">" \
                "<div class=\"chat-question-desc\">关于 SIG信息 你可以问我任何问题,也可以尝试点击以下问题开始：</div>" \
                "<div class=\"chat-question-list\">" \
                "<div class=\"chat-question-list-item\">社区有哪些SIG组</div>" \
                "<div class=\"chat-question-list-item\">查询QA SIG组的仓库清单</div>" \
                "<div class=\"chat-question-list-item\">最近一个月 QA SIG组最活跃的开发者是哪些人</div>" \
                "<div class=\"chat-question-list-item\">查询Infra SIG组主要方向是什么</div>" \
                "<div class=\"chat-question-list-item\">检索Infra SIG组的maintainer和committer联系方式</div>" \
                "</div>" \
                "</div>"

    meeting_scene = "<div class=\"chat-question-content\">" \
                    "<div class=\"chat-question-desc\">关于 会议信息 你可以问我任何问题,也可以尝试点击以下问题开始：</div>" \
                    "<div class=\"chat-question-list\">" \
                    "<div class=\"chat-question-list-item\">社区最近3次会议是哪些</div>" \
                    "<div class=\"chat-question-list-item\">查询QA SIG组近期的会议情况，并且以表格展示</div>" \
                    "</div>" \
                    "</div>"

    community_contribute_scene = "<div class=\"chat-question-content\">" \
                                 "<div class=\"chat-question-desc\">关于 社区贡献 你可以问我任何问题,也可以尝试点击以下问题开始：</div>" \
                                 "<div class=\"chat-question-list\">" \
                                 "<div class=\"chat-question-list-item\">获取openGuass社区贡献指南</div>" \
                                 "<div class=\"chat-question-list-item\">获取openGuass社区,QA SIG组中的pr贡献</div>" \
                                 "<div class=\"chat-question-list-item\">获取openGuass社区,QA SIG组中的issue贡献</div>" \
                                 "<div class=\"chat-question-list-item\">获取openGuass社区,QA SIG组中的comment贡献</div>" \
                                 "</div>" \
                                 "</div>"
    community_data_scene = "<div class=\"chat-question-content\">" \
                           "<div class=\"chat-question-desc\">关于 社区数据 你可以问我任何问题,也可以尝试点击以下问题开始：</div>" \
                           "<div class=\"chat-question-list\">" \
                           "<div class=\"chat-question-list-item\">openguass社区中有哪些SIG组</div>" \
                           "<div class=\"chat-question-list-item\">openguass社区中，一共有多少位issue指派者," \
                           "获取10个issue的指派者信息</div>" \
                           "<div class=\"chat-question-list-item\">openguass社区中，一共有多少位PR贡献者," \
                           "获取10个PR贡献者信息</div>" \
                           "</div>" \
                           "</div>"

    lower_scenes = scenes.lower()
    if 'sig' in lower_scenes:
        return sig_scene
    elif 'pr' in lower_scenes:
        return pr_scenes
    elif '会议查询以及预定' in lower_scenes or 'meeting' in lower_scenes:
        return meeting_scene
    elif '社区贡献' in lower_scenes or 'community_contribution' in lower_scenes or 'contribution' in lower_scenes:
        return community_contribute_scene
    elif '社区数据' in lower_scenes or 'community data' in lower_scenes or 'data' in lower_scenes:
        return community_data_scene
    return "推荐一些通用问题"

@tool
def gitee_user_tool(
    gitee_name: Annotated[str, "从系统提示语中获取gitee_name返回"]
):
    """当您需要获取个人信息时非常有用,比如回答我是谁时, 通过返回值输出分析并得出正确的结果
    output: 您的Gitee用户名为: {gitee_name}
    限制:仅限于上下文有我的字符才能调用该工具
    """
    if 'default_opengauss' == gitee_name:
        return "您没有设置gitee信息，无法识别您的具体信息"
    return "您的Gitee用户名为: {}".format(gitee_name)

SYSTEM_PROMPT = """
- Role: openGauss和openEuler敏感问题过滤专家
- Background: 用户可能对社区有疑问或需要帮助，需要判断问题是否属于该社区领域。
- Profile: 你是一位对社区有深入了解的专家，能够识别和判断问题是否与openGauss和openEuler相关。
- Goals: 设计一个能够准确判断问题是否属于openGauss和openEuler社区领域知识。
- Constrains: 判断必须基于问题的内容，不能依赖于提问者的身份或其他非问题内容的信息。
- OutputFormat: 只回答yes或no，"yes"表示问题属于openGauss社区领域，"no"表示不属于。
- Workflow:
  1. 读取用户的问题。
  2. 分析问题关键词和上下文，判断是否与openGauss和openEuler社区相关。
  3. 根据判断结果输出"yes"或"no"。
- Examples:
  用户问题：openGauss数据库的性能优化有哪些方法？
  判断结果：yes
  用户问题：如何使用Python进行数据分析？
  判断结果：no
  用户问题：openEuler发展怎么样？
  判断结果：yes
- Initialization: 我将帮助您判断这是否属于openGauss和openEuler社区领域的问题。
"""

moderate = OpenAIModerationChain()
model = OpenAI()
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])
chain = prompt | model
moderated_chain = chain | moderate

@tool
def moderation_security_tool(
    input_question: Annotated[str, "需要进行敏感词过滤的用户问题"],
    tool_name: Annotated[str, "敏感词过滤后需要继续调用tool的名字"],
):
    """search_tavily, search_tavily_answer, wikipedia这三个工具调用前必须先调用该工具进行敏感词过滤
       如果不是openGauss社区问题就不要继续回答了
    """
    global moderated_chain
    security = moderated_chain.invoke(input_question)
    if 'no' in security['output']:
        return "您的问题不属于openGauss社区智能小助手的领域范围，结束对话，请不要继续搜索该问题！"
    return "以输入为{}继续调用工具".format(input_question)

@tool
def tavily_answer_tool(
    input: Annotated[str, "输入参数, 不能涉及娱乐、政治、文化、宗教相关问题"]
):
    """执行该工具之前需要先调用moderation_security_tool进行敏感词判断
    """
    tavily_search = TavilySearchAPIWrapper()
    return _TavilyAnswer(api_wrapper=tavily_search, name="search_tavily_answer").run(input)

@tool
def search_tavily(
    input: Annotated[str, "输入参数, 不能涉及娱乐、政治、文化、宗教相关问题"]
):
    """执行该工具之前需要先调用moderation_security_tool进行敏感词判断
    """
    tavily_search = TavilySearchAPIWrapper()
    return TavilySearchResults(api_wrapper=tavily_search, name="search_tavily", max_results=2).run(input)

wikipedia_tool = create_retriever_tool(
        WikipediaRetriever(), "wikipedia", "Search for a query on Wikipedia,调用前必须使用moderation_security_tool敏感词过滤"
    )

@tool
def wikipedia_retriver(
    input: Annotated[str, "输入参数, 不能涉及娱乐、政治、文化、宗教相关问题"]
):
    """执行该工具之前需要先调用moderation_security_tool进行敏感词判断
    """
    return wikipedia_tool.run(input)
