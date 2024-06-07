import os
import requests
import json
from typing import Annotated
from langchain_core.tools import tool

base_issues_url = os.getenv('ISSUES_BASE_URL')

@tool
def get_issues_labels(
    keyword: Annotated[str, "模糊匹配issue的标签, 比如sig/Application，默认不匹配."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，最大上限为100, 超过100后需要做分页查询处理."] = 20,
) -> str:
    """
    - issue标签列表
    """
    url = base_issues_url + "labels"
    # Parameters for the request
    params = {
        'keyword': keyword,
        'page': page,
        'per_page': per_page,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        # raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

@tool
def get_issues_detail_info(
    org: Annotated[str, "issues的所归属的组织，比如openeuler."] = '',
    sig: Annotated[str, "issues的SIG\(Special Interest Groups\)组，比如openeuler/yocto."] = '',
    repo: Annotated[str, "issues的所归属的仓库，比如openeuler/ft_mmi"] = '',
    state: Annotated[str, "issues的当前的状态, 该值可以是open或close."] = '',
    number: Annotated[str, "issues的编号, 比如I9P2O4."] = '',
    author: Annotated[str, "issues提交者"] = '',
    assignee: Annotated[str, "issues的指派者, 比如caodongxia."] = '',
    branch: Annotated[str, "issues的指定分支"] = '',
    label: Annotated[str, "issues的当前的标签, 比如sig/sig-nodejs."] = '',
    exclusion: Annotated[str, "需要过滤的issue标签, 比如sig/sig-ai."] = '',
    issue_state: Annotated[str, "issues的具体状态."] = '',
    issue_type: Annotated[str, "issues的类型."] = '',
    search: Annotated[str, "issues的模糊搜索."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，最大上限为50, 超过50需分页查询,默认2."] = 2,
) -> str:
    """
    - issue列表, 获取issue列表详情
    """
    url = base_issues_url
    # Parameters for the request
    params = {
        'org'        : org,
        'repo'       : repo,
        'sig'        : sig,
        'state'      : state,
        'number'     : number,
        'author'     : author,
        'assignee'   : assignee,
        'branch'     : branch,
        'label'      : label,
        'exclusion'  : exclusion,
        'issue_state': issue_state,
        'issue_type' : issue_type,
        'search'     : search,
        'page'       : page,
        'per_page'   : per_page,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        # raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data
