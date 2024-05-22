import os
import requests
import json
from typing import Annotated
from langchain_core.tools import tool

base_meeting_url = os.getenv('MEET_BASE_URL')

@tool
def get_meetinfo_by_group(
    group: Annotated[str, "获取会议信息的过滤参数，主要通过sig组条件查询，比如CloudNative, 默认为空."] = '',
):
    """
    - 功能描述: 查询社区的会议列表信息和会议详情, 当group为空时，将查询全部会议信息
    """
    url = base_meeting_url + 'meetingsdata/'
    params = {
        'group': group,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data

@tool
def get_all_meeting_group(
    input: Annotated[str, "默认为空"] = '',
):
    """查询会议服务系统中，所有已经预定会议的sig组信息，主要展示了sig组的名称，
       和会议相关的内容时才优先被调用.
    """
    url = base_meeting_url + "groups/"
    print(url)
    ret = requests.get(url)
    if ret.status_code == 200:
        data = ret.json()
    else:
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data

@tool
def create_a_meeting(
    date: Annotated[str, "会议日期\(必填项\)，格式为: 2024-04-15"],
    time_start: Annotated[str, "开始时间\(必填项\)，格式为: 10:00"],
    time_end: Annotated[str, "结束时间\(必填项\)，格式为: 10:30"],
    group_name: Annotated[str, "sig组名称\(必填项\)"],
    sponsor: Annotated[str, "会议发起人\(必填项\)"],
    topic: Annotated[str, "会议议题\(必填项\)"],
    platform: Annotated[str, "会议平台\(必填项\)，如: welink"],
    agenda: Annotated[str, "会议详情"] = '',
    emaillist: Annotated[str, "邮件地址"] = '',
    record: Annotated[str, "是否录制会议"] = '',
    etherpad: Annotated[str, "文档编辑器"] = '',
):
    """在会议服务系统中，创建一个会议，需要指定时间、会议平台、sig组名称、会议议题."""
    token = input("Enter valid token:")
    data = {
        'agenda': agenda,
        'date': date,
        'emaillist': emaillist,
        'end': time_end,
        'etherpad': etherpad,
        'group_name': group_name,
        'join_url': "",
        'platform': platform,
        'record': record,
        'sponsor': sponsor,
        'start': time_start,
        'topic': topic
    }
    res = requests.post(url,
            headers={'Content-Type': 'application/json;charset=UTF-8',
                     'Authorization': 'Bearer {}'.format(token)},
                     json=data
            )
    print('status code: ', res.status_code)
    print('response ', res.json())
