from typing import Annotated, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import app.storage as storage
from app.auth.handlers import AuthedUser
from app.schema import Assistant
from app.agent import DEFAULT_SYSTEM_MESSAGE
import structlog
from datetime import datetime, timezone

router = APIRouter()
logger = structlog.get_logger(__name__)

class AssistantPayload(BaseModel):
    """Payload for creating an assistant."""

    name: str = Field(..., description="The name of the assistant.")
    config: dict = Field(..., description="The assistant config.")
    public: bool = Field(default=False, description="Whether the assistant is public.")


AssistantID = Annotated[str, Path(description="The ID of the assistant.")]


@router.get("/")
async def list_assistants(user: AuthedUser) -> List[Assistant]:
    """List all assistants for the current user."""
    return await storage.list_assistants(user["user_id"])


@router.get("/public/")
async def list_public_assistants() -> List[Assistant]:
    """List all public assistants."""
    return await storage.list_public_assistants()


@router.get("/{aid}")
async def get_assistant(
    user: AuthedUser,
    aid: AssistantID,
) -> Assistant:
    """Get an assistant by ID."""
    assistant = await storage.get_assistant(user["user_id"], aid)
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return assistant


@router.post("")
async def create_assistant(
    user: AuthedUser,
    payload: AssistantPayload,
) -> Assistant:
    """Create an assistant."""
    return await storage.put_assistant(
        user["user_id"],
        str(uuid4()),
        name=payload.name,
        config=payload.config,
        public=payload.public,
    )


@router.put("/{aid}")
async def upsert_assistant(
    user: AuthedUser,
    aid: AssistantID,
    payload: AssistantPayload,
) -> Assistant:
    """Create or update an assistant."""
    return await storage.put_assistant(
        user["user_id"],
        aid,
        name=payload.name,
        config=payload.config,
        public=payload.public,
    )


@router.delete("/{aid}")
async def delete_assistant(
    user: AuthedUser,
    aid: AssistantID,
):
    """Delete an assistant by ID."""
    await storage.delete_assistant(user["user_id"], aid)
    return {"status": "ok"}

async def _create_default_assistant(user_id: str, name: str) -> Assistant:
    """create default assistant"""
    # 复用 gitee_name 作为 assistant 的name
    assistant_name = 'default_opengauss'
    self_info = ""
    if name:
        assistant_name = name
        self_info = "我的gitee_name为:" + name
    default_config = {
        "configurable":{
            "type":"agent",
            "type==agent/agent_type":"GPT 3.5 Turbo",
            "type==agent/interrupt_before_action": False,
            "type==agent/retrieval_description":"Can be used to look up information that was uploaded to this assistant.\n"
                "If the user is referencing particular files, that is often a good hint that information may be here.\n"
                "If the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!",
            "type==agent/system_message":DEFAULT_SYSTEM_MESSAGE + self_info,
                "type==agent/tools":[
                    {
                        "id": "1",
                        "type": "wikipedia",
                        "name": "Wikipedia",
                        "description": "Searches [Wikipedia](https://pypi.org/project/wikipedia/).",
                        "config": {}
                    },
                    {
                        "id": "2",
                        "type": "search_tavily",
                        "name": "Search (Tavily)",
                        "description": "Uses the [Tavily](https://app.tavily.com/) search engine. Includes sources in the response.",
                        "config": {}
                    },
                    {
                        "id": "3",
                        "type": "search_tavily_answer",
                        "name": "Search (short answer, Tavily)",
                        "description": "Uses the [Tavily](https://app.tavily.com/) search engine. This returns only the answer, no supporting evidence.",
                        "config": {}
                    },
                    {
                        "id": "4",
                        "type": "now_time_tool",
                        "name": "get now time",
                        "description": "获取服务器的本地时间.",
                        "config": {}
                    },
                    {
                        "id": "5",
                        "type": "data_state_all_sig",
                        "name": "get datastat all sig",
                        "description": "社区服务运营数据集，可以查询所有的sig组.",
                        "config": {}
                    },
                    {
                        "id": "6",
                        "type": "data_state_sig_detail",
                        "name": "get datastat sig detail",
                        "description": "社区服务运营数据集，可以查询sig组详情，包括miantainer、committer等信息.",
                        "config": {}
                    },
                    {
                        "id": "7",
                        "type": "data_state_contribute",
                        "name": "get datastat contribute",
                        "description": "社区服务运营数据集，可以查询按 pr/issue/coment 维度的贡献值.",
                        "config": {}
                    },
                    {
                        "id": "8",
                        "type": "meet_group",
                        "name": "get all meeting sig group",
                        "description": "获取会议系统的所有sig信息.",
                        "config": {}
                    },
                    {
                        "id": "9",
                        "type": "meet_info",
                        "name": "get a sig meeting detail info",
                        "description": "获取某个sig的会议预定详情.",
                        "config": {}
                    },
                    {
                        "id": "10",
                        "type": "meet_create",
                        "name": "create a meeting",
                        "description": "通过输入信息在会议系统创建一个会议",
                        "config": {}
                    },
                    {
                        "id": "11",
                        "type": "send_email",
                        "name": "send a email",
                        "description": "通过email催促并通知committer或maintainer进行代码检视",
                        "config": {}
                    },
                    {
                        "id": "12",
                        "type": "pull_auther",
                        "name": "get pull by author keyword",
                        "description": "模糊搜索pull提交的人名",
                        "config": {}
                    },
                    {
                        "id": "13",
                        "type": "pull_detail",
                        "name": "get pull detail info",
                        "description": "获取PR的详情",
                        "config": {}
                    },
                    {
                        "id": "14",
                        "type": "pull_label",
                        "name": "get pull label",
                        "description": "获取PR的label信息",
                        "config": {}
                    },
                    {
                        "id": "15",
                        "type": "pull_repo",
                        "name": "get pull repo",
                        "description": "获取PR的代码仓repo, 可通过sig过滤",
                        "config": {}
                    },
                    {
                        "id": "16",
                        "type": "pull_ref",
                        "name": "get pull branch",
                        "description": "模糊搜索PR的分支名",
                        "config": {}
                    },
                    {
                        "id": "17",
                        "type": "pull_sig",
                        "name": "get pull sig",
                        "description": "模糊搜索PR的sig组",
                        "config": {}
                    },
                    {
                        "id": "18",
                        "type": "public_retrieval",
                        "name": "PublicRetrieval",
                        "description": "检索、搜索高优先级使用该工具，检索社区领域知识",
                        "config": {}
                    },
                    {
                        "id": "19",
                        "type": "issue_label",
                        "name": "get issue  all label",
                        "description": "issue标签列表",
                        "config": {}
                    },
                    {
                        "id": "20",
                        "type": "issue_detail",
                        "name": "get issue detail info",
                        "description": "获取issue列表详情",
                        "config": {}
                    },
                    {
                        "id": "21",
                        "type": "issue_assign",
                        "name": "get issue assignee",
                        "description": "获取issue的责任者",
                        "config": {}
                    },
                    {
                        "id": "22",
                        "type": "web_loader",
                        "name": "get web loader by url",
                        "description": "爬取指定URL的内容，获取openGauss的社区贡献指南非常有用",
                        "config": {}
                    },
                    {
                        "id": "23",
                        "type": "recommend_question",
                        "name": "get recommend question",
                        "description": "获取自定义推荐的问题，根据输入场景进行推荐",
                        "config": {}
                    },
                    {
                        "id": "24",
                        "type": "gitee_info",
                        "name": "get gitee user info",
                        "description": "获取gitee的用户信息，当问我是谁时特别有用",
                        "config": {}
                    },
                    {
                        "id": "25",
                        "type": "safety_filter",
                        "name": "filter unsafety input",
                        "description": "过滤非openGauss领域的问题",
                        "config": {}
                    }],
            "type==chat_retrieval/llm_type":"GPT 3.5 Turbo",
            "type==chat_retrieval/system_message":DEFAULT_SYSTEM_MESSAGE + self_info
        }
    }
    return await storage.put_assistant(
        user_id,
        str(uuid4()),
        name=assistant_name,
        config=default_config,
        public=False,
    )

@router.post("/getorcreate")
async def create_assistant(request: Request) -> Assistant:
    """Get or Create an assistant."""
    header = request.headers
    try:
        payload = await request.json()
    except ValueError:
        return JSONResponse(status_code=400, content={"message": "Invalid JSON payload"})
    if 'user_name' not in payload or 'gitee_name' not in payload:
        return JSONResponse(status_code=400, content={"message": "Missing 'user_name' or 'gitee_name' in payload"})
    user_name = payload['user_name']
    user, is_first = await storage.get_or_create_user(user_name)
    logger.info("user:{}, is_first: {}".format(user, is_first))
    try:
        if is_first:
            return await _create_default_assistant(user['user_id'], payload['gitee_name'])
        else:
            assistants = await storage.list_assistants(user["user_id"])
            if not assistants:
                return await _create_default_assistant(user['user_id'], payload['gitee_name'])
            return assistants[0] 
    except Exception as e:
        await storage.delete_user(user["sub"], user["user_id"])
        logger.info("Exception: {}".format(e))
        return JSONResponse(status_code=400, content={"message": "get or create default assistant failed."})

