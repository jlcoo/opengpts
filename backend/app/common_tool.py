from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from datetime import datetime
from typing import Annotated

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
    """当您需要获取场景问答时，非常有用，会返回推荐问题, 保留该tool输出格式
    """
    # 社区贡献
    # 社区数据
    # PR相关
    pr_scenes = """
    <div style="color:red">
    1. 查询我最近在某个sig组提交的PR有哪些，其中有几个是处于open状态？比如:查询我最近在Infra sig组提交的PR有哪些，其中有几个是处于open状态？
    2. 获取某个sig组下的未关闭/已关闭的PR信息?比如:获取QA SIG组下的未关闭的PR信息？
    3. 有提交过PR记录的sig组有哪些？一共多少个？
    4. 查询我在某个sig组最近一次提交的PR，并找到该PR对应SIG的maintainer，发邮件催促maintainer检视该PR。
    5. 获取某个sig组的未关闭/已关闭的issue详情?比如:获取QA SIG组下的未关闭的issue详情？
    </div>
    """
    # Issue相关
    # SIG信息
    sig_scene = """
    <div style="color:red">
    1. 社区有哪些SIG组？
    2. 查询某个SIG组的仓库清单,比如:查询QA SIG组的仓库清单?
    3. 最近一个月 QA SIG组最活跃的开发者是哪些人？
    4. 检索一下某个sig组的maintainer和committer联系方式，比如检索Infra sig组的maintainer和committer联系方式
    5. 查询某个SIG组主要方向是什么?
    </div>
    """
    meeting_scene = """
    <div style="color:red">
    1. 社区最近3次会议是哪些？
    2. 查询某个SIG组最近一周的会议列表,比如:查询QA SIG组最近一周的会议列表？
    3. 查询某个SIG组近期的会议情况，并且以表格展示,比如:查询QA SIG组近期的会议情况，并且以表格展示？
    4. 查询会议服务系统中，所有已经预定会议的sig组信息?
    </div>
    """
    community_contribute_scene = """
    <div style="color:red">
    1. 查询某个SIG组中的pr贡献？比如:查询在QA SIG组中的pr贡献?
    2. 查询某个SIG组中的issue贡献？比如:查询在QA SIG组中的issue贡献？
    3. 查询某个SIG组中的comment贡献？比如:查询在QA SIG组中的comment贡献？
    </div>
    """
    community_data_scene = """
    <div style="color:red">
    1. 在openguass社区中，一共有多少位issue指派者？获取10个issue的指派者信息?
    2. 在openguass社区中，一共有多少位PR贡献者？获取10个PR贡献者信息?
    3. 在openguass社区中有哪些SIG组?
    </div>
    """
    if 'SIG' in scenes or 'sig' in scenes:
        return sig_scene
    elif 'PR' in scenes or 'pr' in scenes:
        return pr_scenes
    elif '会议' in scenes or 'meeting' in scenes or 'MEETING' in scenes:
        return meeting_scene
    elif '社区贡献' in scenes or 'community_contribution' in scenes:
        return community_contribute_scene
    elif '社区数据' in scenes:
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
