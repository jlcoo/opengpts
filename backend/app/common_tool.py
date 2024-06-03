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
def web_loader(url: str) -> str:
    """当您需要获取当前时间非常有效
    """