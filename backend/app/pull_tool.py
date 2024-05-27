import os
import requests
import json
from typing import Annotated
from langchain_core.tools import tool

base_pulls_url = os.getenv('PULL_BASE_URL')

@tool
def get_pulls_labels(
    keyword: Annotated[str, "模糊匹配pull\(pr\)的标签, 比如kind/cleanup，默认不匹配."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
) -> str:
    """
    - Pull Request标签列表
    - 功能介绍
        获取所有Pull Request的标签列表
    - URI
        GET /pulls/labels
    - 示例
        输入示例
        ```
        GET https://ipb.osinfra.cn/pulls/labels?keyword=kind
        ```
        输出示例
        ```
        {
        "total": q,
        "page": 1,
        "per_page": 20,
        "data": [
            "kind/bug",
        ]
        }
        ```
    """
    global base_pulls_url
    url = base_pulls_url + "labels"
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
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data

@tool
def get_pulls_repos(
    sig: Annotated[str, "PR的SIG\(Special Interest Groups\)组，比如community."],
    keyword: Annotated[str, "模糊匹配pull\(pr\)的标签, 比如kind/cleanup，默认不匹配."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
):
    """
    - 功能介绍: 获取所有Pull Request的仓库列表
    - URI: GET /pulls/repos
    - 输入示例: https://ipb.osinfra.cn/pulls/repos?sig=tc
    - 输出示例:
        ```
        {
        "total": 2,
        "page": 1,
        "per_page": 10,
        "data": [
            "openeuler/community",
            "openeuler/TC"
        ]
        }
        ```
    """
    global base_pulls_url
    url = base_pulls_url + "repos"
    # Parameters for the request
    params = {
        'sig': sig,
        'keyword': keyword,
        'page': page,
        'per_page': per_page,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data


@tool
def get_pulls_detail_info(
    org: Annotated[str, "Pull Request所属组织，比如openeuler/opengauss."] = os.getenv('COMMUNITY'),
    sig: Annotated[str, "PR的SIG\(Special Interest Groups\)组，比如sig-K8sDistro."] = '',
    repo: Annotated[str, "PR的所归属的项目或代码仓，比如openeuler/ft_mmi, repo需要加上openeuler前缀"] = '',
    state: Annotated[str, "PR的当前的状态, 该值可以是open、merged、closed, 默认不填."] = '',
    ref: Annotated[str, "Pull Request指定的分支."] = '',
    author: Annotated[str, "PR提交者，不为空时必须通过get_pulls_authors这个接口进行模糊查询，查询结果作为author的输入"] = '',
    assignee: Annotated[str, "PR的指派者, 比如caodongxia."] = '',
    label: Annotated[str, "PR的当前的标签, 比如sig/sig-nodejs."] = '',
    exclusion: Annotated[str, "需要过滤的PR标签, 比如sig/sig-ai."] = '',
    search: Annotated[str, "PR的模糊搜索."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，最大上限为100, 超过100需分页查询."] = 20,
) -> str:
    """
    - 功能介绍: 获取所有开源社区组织下仓库的Pull Request列表，需要放回PR地址
    - output: PR id地址为PR URL地址的数字
    """
    global base_pulls_url
    url = base_pulls_url
    # Parameters for the request
    params = {
        'org'        : org,
        'repo'       : repo,
        'sig'        : sig,
        'state'      : state,
        'ref'        : ref,
        'author'     : author,
        'assignee'   : assignee,
        'label'      : label,
        'exclusion'  : exclusion,
        'search'     : search,
        'page'       : page,
        'per_page'   : per_page,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data

@tool
def get_pulls_assignees(
    keyword: Annotated[str, "模糊匹配pull\(pr\)的指派者, 比如alex，默认不匹配."],
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
):
    """
    - 功能介绍: 获取所有Pull Request指派者的列表
    - URI: GET /pulls/assignees
    - 输出示例:
        {
        "total": 2,
        "page": 1,
        "per_page": 20,
        "data": [
            "AlexZ11",
            "alexanderbill"
        ]
        }
        ```
    """
    global base_pulls_url
    url = base_pulls_url + "assignees"
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
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data

@tool
def get_pulls_authors(
    keyword: Annotated[str, "模糊匹配pull\(pr\)的作者或提交人, 比如alex，默认不匹配."],
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
):
    """
      - 功能介绍: 获取所有Pull Request提交人的列表, 有PR作者(authors)时，这个可接需要有限被模糊查询调用
      - URI: GET /pulls/authors
      - 输出示例:
        ```
        {
          "total": 67,
          "page": 1,
          "per_page": 20,
          "data": [
            "a_night_of_baldness",
            "alapha",
            "albert-lee-7",
          ]
        }
        ```
    """
    # 先直接 return,[TODO]接口OK后需要删除
    return keyword
    global base_pulls_url
    url = base_pulls_url + "authors"
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
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

@tool
def get_pulls_refs(
    keyword: Annotated[str, "模糊匹配pull\(pr\)的分支名, 比如alex，默认不匹配."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
):
    """
    - 功能介绍: 获取所有Pull Request的分支列表
    - URI: GET /pulls/refs
    - 输出示例
        ```
        {
        "total": 5,
        "page": 1,
        "per_page": 10,
        "data": [
            "Multi-Version_obs-server-2.10.11_openEuler-22.09",
            "openEuler-22.09",
            "openEuler-22.09-HCK",
            "openEuler-22.09-next",
            "sync-pr214-openEuler-22.03-LTS-to-openEuler-22.09"
        ]
        }
        ```
    """
    global base_pulls_url
    url = base_pulls_url + "refs"
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
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data

@tool
def get_pulls_sigs(
    keyword: Annotated[str, "模糊匹配pull\(pr\)的sig组, 比如alex，默认不匹配，获取PR记录的SIG组非常有用."] = '',
):
    """
    - 功能介绍: 获取有PR记录的所有SIG的列表，获取SIG列表优先被调用
    - URI: GET /pulls/sigs
    - 输出示例:
    ```
    {
        "code": 200,
        "msg": "请求成功",
        "data": [
        "Compiler",
        "Computing",
        "security-committee",
        "sig-compat-winapp",
        "sig-Compatibility-Infra",
        "sig-compliance",
        "sig-confidential-computing",
        "user-committee"
        ]
    }
    """
    global base_pulls_url
    url = base_pulls_url + "sigs"
    # Parameters for the request
    params = {
        'keyword': keyword,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data
