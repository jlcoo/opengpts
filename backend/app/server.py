import os
from pathlib import Path

import orjson
import structlog
from fastapi import FastAPI, Form, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles

import app.storage as storage
import logging
from app.api import router as api_router
from app.auth.handlers import AuthedUser
from app.lifespan import lifespan
from app.upload import convert_ingestion_input_to_blob, ingest_runnable

logger = structlog.get_logger(__name__)

class IgnoreChangeDetectedFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return '%d change%s detected: %s' != record.msg
# logger.addFilter(IgnoreChangeDetectedFilter())
# root_logger = logger.getLogger()
# root_logger.addFilter(IgnoreChangeDetectedFilter())

app = FastAPI(title="OpenGPTs API", lifespan=lifespan)


# Get root of app, used to point to directory containing static files
ROOT = Path(__file__).parent.parent


app.include_router(api_router)


@app.post("/ingest", description="Upload files to the given assistant.")
async def ingest_files(
    files: list[UploadFile], user: AuthedUser, config: str = Form(...)
) -> None:
    """Ingest a list of files."""
    config = orjson.loads(config)

    assistant_id = config["configurable"].get("assistant_id")
    if assistant_id is not None:
        assistant = await storage.get_assistant(user["user_id"], assistant_id)
        if assistant is None:
            raise HTTPException(status_code=404, detail="Assistant not found.")

    thread_id = config["configurable"].get("thread_id")
    if thread_id is not None:
        thread = await storage.get_thread(user["user_id"], thread_id)
        if thread is None:
            raise HTTPException(status_code=404, detail="Thread not found.")

    file_blobs = [convert_ingestion_input_to_blob(file) for file in files]
    return ingest_runnable.batch(file_blobs, config)

@app.post("/ragfiles", description="git clone docs to rag vector")
async def rag_files(
    user: AuthedUser, config: str = Form(...)
) -> None:
    """Ingest a list of files."""
    config = orjson.loads(config)

    assistant_id = config["configurable"].get("assistant_id")
    logger.info("assistant_id: {} user id: {}".format(assistant_id, user["user_id"]))

    if assistant_id is not None:
        assistant = await storage.get_assistant(user["user_id"], assistant_id)
        if assistant is None:
            raise HTTPException(status_code=404, detail="Assistant not found.")

    thread_id = config["configurable"].get("thread_id")
    if thread_id is not None:
        thread = await storage.get_thread(user["user_id"], thread_id)
        if thread is None:
            raise HTTPException(status_code=404, detail="Thread not found.")

    return ingest_runnable.invoke_markdown(config)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


ui_dir = str(ROOT / "ui")

if os.path.exists(ui_dir):
    app.mount("", StaticFiles(directory=ui_dir, html=True), name="ui")
else:
    logger.warn("No UI directory found, serving API only.")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)
