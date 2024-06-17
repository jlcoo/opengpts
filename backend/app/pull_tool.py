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
    """
    global base_pulls_url
    url = base_pulls_url + "labels"
    if keyword == 'all' or keyword == 'total':
        keyword = ''
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
def get_pulls_repos(
    sig: Annotated[str, "PR的SIG\(Special Interest Groups\)组，比如community."],
    keyword: Annotated[str, "模糊匹配pull\(pr\)的标签, 比如kind/cleanup，默认不匹配."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
):
    """
    - 功能介绍: 获取所有Pull Request的仓库列表
    """
    global base_pulls_url
    url = base_pulls_url + "repos"
    if keyword == 'all' or keyword == 'total':
        keyword = ''
    # Parameters for the request
    params = {}
    if sig == 'all':
        params = {
            'keyword': keyword,
            'page': page,
            'per_page': per_page,
        }
    else:
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
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data


@tool
def get_pulls_detail_info(
    sig: Annotated[str, "PR的SIG组，比如Infra."],
    org: Annotated[str, "Pull Request所属组织，比如openeuler/opengauss."] = os.getenv('COMMUNITY'),
    repo: Annotated[str, "PR的所归属的项目或代码仓，比如openeuler/ft_mmi, repo需要加上openeuler前缀"] = '',
    state: Annotated[str, "PR的当前的状态, 该值可以是open、merged、closed, 默认不填."] = '',
    ref: Annotated[str, "Pull Request指定的分支."] = '',
    author: Annotated[str, "PR提交者，不为空时必须通过get_pulls_authors这个接口进行模糊查询，查询结果作为author的输入"] = '',
    label: Annotated[str, "PR的当前的标签, 比如sig/sig-nodejs."] = '',
    exclusion: Annotated[str, "需要过滤的PR标签, 比如sig/sig-ai."] = '',
    search: Annotated[str, "PR的模糊搜索."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，最大上限为100, 超过100需分页查询."] = 2,
) -> str:
    """
    - 功能介绍: 获取所有开源社区组织下仓库的Pull Request列表，需要放回PR地址
    - output: PR id地址为PR URL地址的数字
    """
    global base_pulls_url
    if sig == 'all':
        return "先调用get_pulls_sig获取所有sig组，再将per_page设置为1调用get_pulls_detail_info"
    if state == 'all':
        state = ''
    url = base_pulls_url
    # Parameters for the request
    params = {
        'org'        : org,
        'repo'       : repo,
        'sig'        : sig,
        'state'      : state,
        'ref'        : ref,
        'author'     : author,
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
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

@tool
def get_issue_assignees(
    keyword: Annotated[str, "模糊匹配issue的指派者, 比如alex，默认不匹配."],
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
):
    """
    - 功能介绍: 获取所有issue指派者的列表
    """
    global base_pulls_url
    url = base_pulls_url + "assignees"
    if keyword == 'all' or keyword == 'total' or keyword == 'opengauss':
        keyword = ''
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
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

@tool
def get_pulls_authors(
    keyword: Annotated[str, "模糊匹配pull\(pr\)的作者或提交人, 比如alex，默认不匹配."],
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
):
    """
      - 功能介绍: 获取所有Pull Request提交人的列表, 有PR作者(authors)时，这个可接需要有限被模糊查询调用
    """
    # 先直接 return,[TODO]接口OK后需要删除
    global base_pulls_url
    url = base_pulls_url + "authors"
    if keyword == 'all' or keyword == 'total' or keyword == 'opengauss':
        keyword = ''
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
        # return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
        return keyword
    return data

@tool
def get_pulls_refs(
    keyword: Annotated[str, "模糊匹配pull\(pr\)的分支名, 比如alex，默认不匹配."] = '',
    page: Annotated[int, "获取的第几页数，默认1."] = 1,
    per_page: Annotated[int, "每页能获取的数量，默认每次获取20个, 最大上限为100, 超过100后需要做分页查询处理."] = 20,
):
    """
    - 功能介绍: 获取所有Pull Request的分支列表
    """
    global base_pulls_url
    url = base_pulls_url + "refs"
    if keyword == 'all' or keyword == 'total':
        keyword = ''
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
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

@tool
def get_pulls_sigs(
    keyword: Annotated[str, "模糊匹配pull\(pr\)的sig组, 输入不能是人名,只能是可能存在的sig组."] = '',
):
    """
    - 功能介绍: 获取有PR记录的所有SIG的列表，获取SIG列表优先被调用
    """
    global base_pulls_url
    params = {}
    if keyword and keyword != 'all' and keyword != 'total':
        params['keyword'] = keyword
    url = base_pulls_url + "sigs"

    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    print(json.dumps(data))
    return data
