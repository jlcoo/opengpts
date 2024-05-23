import io
import mimetypes
import os
import subprocess
import markdown
from typing import Annotated, List
from fastapi import UploadFile
from langchain_core.document_loaders.blob_loaders import Blob
from app.upload import convert_ingestion_input_to_blob

base_tc_path = os.getenv('TC_REPO_PATH')
os_community = os.getenv('COMMUNITY')

def find_markdown_files(directory):
    """
    递归遍历目录并打印所有 Markdown 文件的绝对路径。
    
    参数:
    directory (str): 要遍历的根目录路径。
    """
    outpath = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                outpath.append(os.path.abspath(os.path.join(root, file)))
                # print(os.path.abspath(os.path.join(root, file)))
    return outpath

def get_all_md_files():
    base_dirs = base_tc_path + os_community + '/'
    if not os.path.exists(base_dirs):
        try:
            os.makedirs(base_dirs)
        except OSError as error:
            print(error)
    tc_path = base_dirs + 'tc/'
    execute_cmd = ''
    if os.path.exists(tc_path):
        # 如果存在则 git pull
        execute_cmd = "cd {} && git pull --rebase && cd -".format(tc_path)
    else:
        # 不存在先clone
        execute_cmd = "cd {} && git clone https://gitee.com/opengauss/tc && cd -".format(base_dirs)
    print(execute_cmd)
    # 使用 subprocess.run 执行命令
    result = subprocess.run(execute_cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError("clone object failed, err:{}".format(result.stderr))
    
    return find_markdown_files(tc_path)

def get_blob_from_markdown():
    blobs = []
    md_path = get_all_md_files()

    for markdown_file_path in md_path:
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()

        # 确定文件类型 (Mime Type)
        mime_type, _ = mimetypes.guess_type(markdown_file_path)
        if not mime_type:
            mime_type = 'text/markdown'  # 默认 Mime Type
        html_text = markdown.markdown(md_text)
        # 创建一个包含文件内容的 Blob 对象
        # file_like_object = io.BytesIO(markdown_content)
        file_like_object = io.BytesIO(html_text.encode('utf-8'))
        mock_upload_file = UploadFile(
            file=file_like_object,
            filename=markdown_file_path,
            # content_type='text/markdown',
            # file_type="md"
        )
        blobs.append(convert_ingestion_input_to_blob(mock_upload_file))
    
    return blobs