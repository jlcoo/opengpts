import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from langchain_core.tools import tool
from urllib.parse import urlparse
from typing import Annotated, List
import structlog
from datetime import datetime, timezone, timedelta
from app.lifespan import get_pg_pool
import asyncio
from typing_extensions import TypedDict

logger = structlog.get_logger(__name__)

class PrEmail(TypedDict):
    url: str
    """pr to send email url."""
    last_send_date: datetime
    """The last time the thread was updated."""

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

async def get_email_last_time(url: str) -> List[PrEmail]:
    """Return last update time"""
    async with get_pg_pool().acquire() as conn:
        return await conn.fetch('SELECT * FROM pr_email WHERE email_key = $1', url)

async def put_pr_email(url: str):
    """Return last update time"""
    updated_at = datetime.now(timezone.utc)
    async with get_pg_pool().acquire() as conn:
        await conn.execute(
            (
                "INSERT INTO pr_email (email_key, last_send_date) VALUES ($1, $2)"
                "ON CONFLICT (email_key) DO NOTHING"
            ),
            url,
            updated_at,
        )

async def update_pr_email_time(url: str, now_time: datetime):
    """Return last update time"""
    async with get_pg_pool().acquire() as conn:
        await conn.execute(
            (
                "UPDATE pr_email SET last_send_date = $1 WHERE email_key = $2"
                "ON CONFLICT (email_key) DO NOTHING"
            ),
            now_time,
            url,
        )

async def get_current_time():
    return datetime.now(timezone.utc)

@tool
async def reminder_reveiw_code(
    repo: Annotated[str, "代码仓库名"],
    url: Annotated[str, "pr 的url地址"],
    state: Annotated[str, "pr 的状态"],
    email: Annotated[str, "检视人的邮箱地址，最好通过社区详情接口获取对应检视人的联系方式"],
    pr_id: Annotated[str, "需要被检视的pr id"],
    title: Annotated[str, "需要被检视的pr内容概要"],
    reviewer: Annotated[str, "代码检视人, reviewers包括maintainer和committers, 或直接从repos详细内容接口获取"],
    developer: Annotated[str, "该PR的作者"] = '',
):
    """
    功能: 当你有PR需要检视时，发邮件提醒maintainer、committer帮忙检视非常有用, 
    推荐: 当有多个检视人需要被提醒时，reminder_reveiw_code 这个工具应该被多次调用,
    检视人联系方式获取: 需要调用自定义工具读 readme 文件或查询社区datastat sig detail获取
    限制: 相同PR的 url 地址，一天只能发送一次，帮我做这个工具的限制
    """
    if state != 'open':
        return "该PR的状态是 {}，请选择open状态的PR通知committer进行检视".format(state)
    if not is_valid_url(url):
        return "pr 地址{}不合法，请重新输入合法有效 PR 的 url 地址".format(url)
    now_date = await get_current_time()
    last_premail = await get_email_last_time(url)
    logger.info(f"last_premail sent to 检视人（{last_premail} {now_date}）")
    if not last_premail:
        await put_pr_email(url)
    else:
        duration = now_date - last_premail[0]['last_send_date']
        if duration < timedelta(days=1) and duration > timedelta(minutes=2):
            return "pr 地址 {} 已经在 {} 时刻发送过了通知检视人的邮件，请您耐心等待，如仍未处理，请一天后重试！"\
                    .format(url, last_premail[0]['last_send_date'])
    # config
    sender = os.getenv('EMAIL_SENDER')  # 更换为当前邮件列表的地址
    recipients = [email]  # 更改为自己的邮箱地址
    subject = '【PR 检视提醒】PR #{} 需要您的检视 - [{}项目]'.format(pr_id, repo)
    message = MIMEMultipart()
    message["Subject"] = Header(subject, 'utf-8')
    ip = os.getenv('EMAIL_SERVICE_IP')  # 接受服务的ip, 不改
    port = os.getenv('EMAIL_PORT')
    ssl_port = os.getenv('EMAIL_SSL_PORT')
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')

    # 邮件正文内容
    mail_body = """尊敬的检视者、commiter、maintainer {}:
        \t您好！我是 {} 的开发者{}。我提交了一个Pull Request（PR #{}，标题为: {}），希望您能抽空检视。
    我非常期望能在一天后得到您的反馈。
        \tPR链接：{}

        \t感谢您的时间和支持。祝好！{}
    """.format(reviewer, repo, developer, pr_id, title, url, developer)
    message.attach(MIMEText(mail_body, "plain", "utf-8"))

    try:
        smtp_obj = smtplib.SMTP(ip, port)
        smtp_obj.login(username, password)
        for recipient in recipients:
            message['To'] = recipient
            text = message.as_string()
            # smtp_obj.sendmail(sender, recipient, text)
            smtp_obj.sendmail(sender, "1417700745@qq.com", text)
        logger.info(f"Email sent to 检视人（{reviewer} {recipients}）")
        if last_premail and now_date - last_premail[0]['last_send_date'] > timedelta(minutes=2):
            await update_pr_email_time(url, now_date)
        return f"已向检视人：{reviewer}，发送PR检视提醒邮件成功，请您耐心等待！"
    except Exception as e:
        print(e)
        print("Testing Scenarios: port:25, is_starttls: no, is_logins: no, result: fault")
        return f"发送PR检视提醒邮件失败，请调整输入稍后再试"
