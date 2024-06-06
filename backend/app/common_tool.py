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
    1. 我最近提交的前5个PR是哪些？其中有几个还是处于open状态？
    2. 有提交过PR记录的sig组有哪些？一共多少个？
    3. 查询我最近一次提交的PR，并找到该PR对应SIG的maintainer和committer，发邮件催促maintainer检视该PR。
    </div>
    """
    # Issue相关
    # SIG信息
    sig_scene = """
    <div style="color:red">
    1. 社区有哪些SIG组？
    2. 社区有哪些SIG组最近一周有会议议程？
    3. 最近一个月 QA SIG组最活跃的开发者是哪些人？
    4. 检索一下某个sig组的maintainer和committer联系方式，比如检索infra sig组的maintainer和committer联系方式
    </div>
    """

    if 'SIG' in scenes or 'sig' in scenes:
        return sig_scene
    elif 'PR' in scenes or 'pr' in scenes:
        return pr_scenes
    return "推荐一些通用问题"

@tool
def gitee_user_tool(
    gitee_name: Annotated[str, "从系统提示语中获取gitee_name返回"]
):
    """当您需要获取个人信息时非常有用,比如回答我是谁时, 通过返回值输出分析并得出正确的结果
    output: 您的Gitee用户名为: jl-brother1
    """
    return "您的Gitee用户名为: {}".format(gitee_name)
