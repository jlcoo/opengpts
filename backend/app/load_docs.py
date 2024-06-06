import io
import mimetypes
import os
import subprocess
import markdown
from typing import Annotated, List
from fastapi import UploadFile
from langchain_core.document_loaders.blob_loaders import Blob
from langchain_community.document_loaders import UnstructuredMarkdownLoader
import structlog
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import os

logger = structlog.get_logger(__name__)

base_tc_path = os.getenv('TC_REPO_PATH')
os_community = os.getenv('COMMUNITY')
    
def load_and_documents(directory_path):
    glob_pattern="./*.md"
    documents = []
    all_sections = []

    loader = DirectoryLoader(directory_path, glob=glob_pattern, silent_errors=True, recursive=True, use_multithreading=True,
                                show_progress=True, loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()

    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3"), ("####", "Header 4")]
    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    for doc in documents:
        sections = text_splitter.split_text(doc.page_content)
        all_sections.append(sections)
    
    return all_sections

def get_md_files_sections():
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
    # print(execute_cmd)
    # 使用 subprocess.run 执行命令
    result = subprocess.run(execute_cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError("clone object failed, err:{}".format(result.stderr))
    
    sections = load_and_documents(tc_path)

    return sections


