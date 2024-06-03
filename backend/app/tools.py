import os
from enum import Enum
from functools import lru_cache
from typing import Optional, Annotated

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.retriever import create_retriever_tool
from langchain_community.retrievers.kay import KayAiRetriever
from langchain_community.retrievers.wikipedia import WikipediaRetriever
from langchain_community.tools.tavily_search import (
    TavilyAnswer as _TavilyAnswer,
)
from langchain_community.tools.tavily_search import (
    TavilySearchResults,
)
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.tools import Tool
from typing_extensions import TypedDict

from app.upload import vstore

from app.datastat_wrap import *
from app.meeting_tool import *
from app.email_tool import reminder_reveiw_code
from app.pull_tool import *
from app.issue_tool import *
from app.common_tool import *
import structlog

logger = structlog.get_logger(__name__)

class AvailableTools(str, Enum):
    TAVILY = "search_tavily"
    TAVILY_ANSWER = "search_tavily_answer"
    RETRIEVAL = "retrieval"
    WIKIPEDIA = "wikipedia"
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
    PULL_LABEL = "pull_label"
    PULL_REPO = "pull_repo"
    PULL_REF = "pull_ref"
    PULL_SIG = "pull_sig"
    PUBLIC_RETRIEVAL = "public_retrieval"
    ISSUE_LABEL = "issue_label"
    ISSUE_DETAIL = "issue_detail"
    ISSUE_ASSIGN = "issue_assign"
    WEB_LOADER = "web_loader"
    USER_INFO = "user_info"


class ToolConfig(TypedDict):
    ...

class BaseTool(BaseModel):
    type: AvailableTools
    name: Optional[str]
    description: Optional[str]
    config: Optional[ToolConfig]
    multi_use: Optional[bool] = False

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
    description: str = Field("检索、搜索高优先级使用该工具，检索社区领域知识", const=True)

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

class PullLabel(BaseTool):
    type: AvailableTools = Field(AvailableTools.PULL_LABEL, const=True)
    name: str = Field("get pull label", const=True)
    description: str = Field(
        "获取PR的label信息",
        const=True,
    )

class PullRepo(BaseTool):
    type: AvailableTools = Field(AvailableTools.PULL_REPO, const=True)
    name: str = Field("get pull repo", const=True)
    description: str = Field(
        "获取PR的代码仓repo, 可通过sig过滤",
        const=True,
    )

class IssueAssign(BaseTool):
    type: AvailableTools = Field(AvailableTools.ISSUE_ASSIGN, const=True)
    name: str = Field("get issue assignee", const=True)
    description: str = Field(
        "获取issue的责任者",
        const=True,
    )

class PullBranch(BaseTool):
    type: AvailableTools = Field(AvailableTools.PULL_REF, const=True)
    name: str = Field("get pull branch", const=True)
    description: str = Field(
        "模糊搜索PR的分支名",
        const=True,
    )

class PullSig(BaseTool):
    type: AvailableTools = Field(AvailableTools.PULL_SIG, const=True)
    name: str = Field("get pull sig", const=True)
    description: str = Field(
        "模糊搜索PR的sig组",
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

class UserInfo(BaseTool):
    type: AvailableTools = Field(AvailableTools.USER_INFO, const=True)
    name: str = Field("get user info", const=True)
    description: str = Field(
        "获取用户信息，主要是openGauss的用户名和gitee的用户名",
        const=True,
    )

RETRIEVAL_DESCRIPTION = """Can be used to look up information that was uploaded to this assistant.
If the user is referencing particular files, that is often a good hint that information may be here.
If the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!"""

PUBLIC_RETRIEVAL_DES = """"
- Role: openGauss社区贡献者和维护者信息检索专家, 高优先级使用该搜索工具
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

def _get_now_time():
    return now_time_tool

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

@lru_cache(maxsize=1)
def _get_pull_label():
    return get_pulls_labels

@lru_cache(maxsize=1)
def _get_pull_repo():
    return get_pulls_repos

@lru_cache(maxsize=1)
def _get_issue_assign():
    return get_issue_assignees

@lru_cache(maxsize=1)
def _get_pull_ref():
    return get_pulls_refs

@lru_cache(maxsize=1)
def _get_pull_sig():
    return get_pulls_sigs

@lru_cache(maxsize=3)
def _get_issue_label():
    return get_issues_labels

@lru_cache(maxsize=1)
def _get_issue_detail():
    return get_issues_detail_info

TOOLS = {
    AvailableTools.TAVILY: _get_tavily,
    AvailableTools.WIKIPEDIA: _get_wikipedia,
    AvailableTools.TAVILY_ANSWER: _get_tavily_answer,
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
    AvailableTools.PULL_LABEL: _get_pull_label,
    AvailableTools.PULL_REPO: _get_pull_repo,
    AvailableTools.PULL_REF: _get_pull_ref,
    AvailableTools.PULL_SIG: _get_pull_sig,
    AvailableTools.PUBLIC_RETRIEVAL: get_retrieval_tool,
    AvailableTools.ISSUE_LABEL: _get_issue_label,
    AvailableTools.ISSUE_DETAIL: _get_issue_detail,
    AvailableTools.ISSUE_ASSIGN: _get_issue_assign,
    AvailableTools.WEB_LOADER: _get_web_loader,
    AvailableTools.USER_INFO: _get_web_loader,
}
