import os
import requests
import json
from typing import Annotated, List
from langchain_core.tools import tool, BaseTool
import subprocess

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
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data

@tool
def query_community_usercontribute(
    sig: Annotated[str, "指定该开源社区下的某个sig组."],
    contributeType: Annotated[str, "开发者贡献类型，可以是pr(合并请求)、issue(需求&问题)、comment(评审)."] = 'pr',
    timeRange: Annotated[str, "指定某个时间范围段，可以是all、lastonemonth、lasthalfyear、lastoneyear."] = 'all',
):
    """
    - 功能介绍：获取所有开源社区下某个sig组，指定贡献范围(pr, issue, comment), 指定时间段的贡献值详情
    """
    url = datastat_base_url + 'usercontribute'
    params = {
        'sig': sig,
        'contributeType': contributeType,
        'timeRange': timeRange,
        'community': os_community,
    }
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
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
    print("url{url} params{params}")
    ret = requests.get(url, params=params)
    if ret.status_code == 200:
        data = ret.json()
    else:
        raise Exception(f"API Request failed with status code: {ret.status_code}")
    print(json.dumps(data))
    return data

@tool
def read_readme_content(
    sig: Annotated[str, "指定该开源社区下的某个sig组, 如果没有指定就会返回该开源社区的所有信息."] = 'all',
):
    """
    - 功能介绍：opengauss社区通过配置文件readme.md获取sig组下的详细内容，比如某个sig组下的maintainers、committers等详细信息，
        特别是获取检视人 reviewers 的联系方式 email 时特别有用
    - 限制: 只对 opengauss 提供该方法，并且优先级最高
    """
    tc_path = base_tc_path + 'tc/'
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
        execute_cmd = "cd {} && git clone https://gitee.com/opengauss/tc && cd -".format(base_tc_path)
    print(execute_cmd)
    # 使用 subprocess.run 执行命令
    result = subprocess.run(execute_cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError("clone object failed, err:{}".format(result.stderr))

    if not os.path.exists(filename):
        return "该 {} {} 在 https://gitee.com/opengauss/tc 不存在，请重新输入".format(sig, filename)

    # 打开文件并读取内容
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    return content

