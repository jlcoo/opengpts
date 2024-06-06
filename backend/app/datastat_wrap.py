import os
import requests
import json
from typing import Annotated, List
from langchain_core.tools import tool, BaseTool
import subprocess
import threading

datastat_base_url = os.getenv('DATASTAT_BASE_URL')
os_community = os.getenv('COMMUNITY')
base_tc_path = os.getenv('TC_REPO_PATH')

@tool
def query_community_detail_info(
    sig: Annotated[str, "指定该开源社区下的某个sig组, 如果没有指定就会返回该开源社区的所有信息."] = '',
):
    """
    - 功能介绍：获取所有开源社区的详细信息，比如某个sig组下的maintainers、committers等详细信息，
        特别是获取检视人 reviewers 的联系方式时特别有用
    """
    url = datastat_base_url + 'info'
    params = {
        'community': os_community,
        'sig': sig,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

@tool
def query_community_usercontribute(
    sig: Annotated[str, "指定该开源社区下的某个sig组."],
    contributeType: Annotated[str, "开发者贡献类型，可以是pr(合并请求)、issue(需求&问题)、comment(评审)."] = 'pr',
    timeRange: Annotated[str, "时间范围段，取值为'all','last_month','last_year','last_6_months'其中一个."] = 'all',
    filter_num: Annotated[int, "过滤贡献值个数."] = 3,
):
    """
    - 功能介绍：获取所有开源社区下某个sig组，指定贡献范围(pr, issue, comment), 指定时间段的贡献值详情
    - 提示: 贡献值使用输出中contribute进行评判
    """
    url = datastat_base_url + 'usercontribute'
    if sig == 'all':
        return "需要先获取一下所有的sig组，并指定某个sig组进一个一个地查询，最多查15个sig, 没有查完的提示下一次回话继续查询"
    if contributeType == 'all':
        return "contributeType 只能填pr, issue和comment，需要一个一个地查询"
    timeList = ['all', 'lastonemonth', 'lasthalfyear', 'lastoneyear']
    if timeRange not in timeList:
        if timeRange == "last_month":
            timeRange = 'lastonemonth'
        elif timeRange == "last_year":
            timeRange = 'lastoneyear'
        elif '6' in timeRange:
            timeRange = 'lasthalfyear'
        else:
            timeRange = 'lastonemonth'
    params = {
        'sig': sig,
        'contributeType': contributeType,
        'timeRange': timeRange,
        'community': os_community,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        try:
            data = ret.json()
            if not data['data']:
                return '调用query_community_all_sigs工具匹配{}相关的sig组'.format(sig)
            filtered_data = [user for user in data['data'] if user['contribute'] >= filter_num]
            sorted_data = sorted(filtered_data, key=lambda x: x['contribute'], reverse=True)
            data['data'] = sorted_data[:20]
        except Exception as e:
            return "输入信息暂时无法处理，请重新调整输入再重试。"
    else:
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

@tool
def query_community_all_sigs(
    community: Annotated[str, "指定某个开源社区的名字."] = '',
):
    """
    - 功能介绍：获取所有开源社区下所有sig组名称
    """
    url = datastat_base_url + 'name'
    # url = 'https://datastat-opengauss.osinfra.cn/query/sig/' + 'name'
    params = {
        'community': os_community,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        try:
            data = ret.json()
        except Exception as e:
            return "输入信息暂时无法处理，请重新调整输入再重试。"
    else:
        #raise Exception(f"API Request failed with status code: {ret.status_code}")
        return "参数错误，请重试，温馨提示，输入信息请尽量准确！status code: {}".format(ret.status_code)
    return data

def read_readme_content_(
    sig: Annotated[str, "指定该开源社区下的某个sig组, 如果没有指定就会返回该开源社区的所有信息."] = 'all',
):
    """
    - 功能介绍：opengauss社区通过配置文件readme.md获取sig组下的详细内容，比如某个sig组下的maintainers、committers等详细信息，
        特别是获取检视人 reviewers 的联系方式 email 时特别有用
    - 限制: 只对 opengauss 提供该方法，并且优先级最高
    """
    base_dirs = base_tc_path + os_community + '/'
    if not os.path.exists(base_dirs):
        try:
            os.makedirs(base_dirs)
        except OSError as error:
            print(error)
    tc_path = base_dirs + 'tc/'
    filename = ''
    if sig == 'all':
        filename = tc_path + 'sigs/README.md'
    elif sig == 'tc':
        filename = tc_path + 'README.md'
    else:
        filename = tc_path + 'sigs/' + sig + '/README.md'

    execute_cmd = ''
    if os.path.exists(tc_path):
        # 如果存在则 git pull
        execute_cmd = "cd {} && git pull --rebase && cd -".format(tc_path)
    else:
        # 不存在先clone
        execute_cmd = "cd {} && git clone https://gitee.com/opengauss/tc && cd -".format(base_dirs)
    # print(execute_cmd)
    # 使用 subprocess.run 执行命令
    result = subprocess.run(execute_cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError("clone object failed, err:{}".format(result.stderr))

    if not os.path.exists(filename):
        return "该 {} {} 在 https://gitee.com/opengauss/tc 不存在，结束该轮对话，请重新输入".format(sig, filename)

    # 打开文件并读取内容
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    return content

lock = threading.Lock()

@tool
def read_readme_content(
    sig: Annotated[str, "指定该开源社区下的某个sig组, 如果没有指定就会返回该开源社区的所有信息."] = 'all',
):
    """
    - 功能介绍：opengauss社区通过配置文件readme.md获取sig组下的详细内容，比如某个sig组下的maintainers、committers等详细信息，
        特别是获取检视人 reviewers 的联系方式 email 时特别有用
    - 限制: 只对 opengauss 提供该方法，并且优先级最高
    """
    with lock:
        return read_readme_content_(sig)
