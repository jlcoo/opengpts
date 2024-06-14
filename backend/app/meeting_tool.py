import os
import requests
import json
from datetime import datetime
from typing import Annotated
from langchain_core.tools import tool

base_meeting_url = os.getenv('MEET_BASE_URL')

@tool
def get_meetinfo_by_group(
    group: Annotated[str, "指定sig,查看该sig组的会议议程详细."] = '',
    day: Annotated[int, "会议系统最新的天数."] = 5,
):
    """
    - 约束: 如果上下文有时间信息，先调用now_time_tool获取一下当前时间,上下文有openGuass社区信息直接调用get_meetinfo_by_group
    """
    if group == 'all' or group == 'openGuass':
        group = ''
    url = base_meeting_url + 'meetingsdata/'
    params = {
        'group': group,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
        # 将字符串日期转换为datetime对象以便于比较
        def parse_date(date_str):
            return datetime.strptime(date_str, "%Y-%m-%d")

        # 按照日期降序排序tableData
        if data['tableData']:
            sorted_table_data = sorted(data["tableData"], key=lambda x: parse_date(x["date"]), reverse=True)
            data['tableData'] = sorted_table_data[:day]
    else:
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

@tool
def get_all_meeting_group(
    input: Annotated[str, "默认为空"] = '',
):
    """查询会议服务系统中，所有已经预定会议的sig组信息，主要展示了sig组的名称."""
    url = base_meeting_url + "groups/"
    ret = requests.get(url)
    if ret.status_code == 200:
        data = ret.json()
    else:
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
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
    # token = input("Enter valid token:")
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
    return "会议预定功能请移步到openGauss官网页面进行操作，会议系统在官网的社区会议板块，openGauss的官网地址为: https://opengauss.org/zh/"
    res = requests.post(url,
            headers={'Content-Type': 'application/json;charset=UTF-8',
                     'Authorization': 'Bearer {}'.format(token)},
                     json=data
            )
    print('status code: ', res.status_code)
    print('response ', res.json())
