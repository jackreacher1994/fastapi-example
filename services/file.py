import shutil
import uuid
import logging

from fastapi import UploadFile
from pathlib import Path

from database import get_current_session, transactional
from models import FileCreate, File
from worker import upload_task

logger = logging.getLogger(__name__)

class FileService:

    @transactional
    async def upload(self, client_id: str, files: list[UploadFile]) -> list[FileCreate]:
        session = get_current_session()

        results: list[FileCreate] = []

        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        for file in files:
            file_id = str(uuid.uuid4())

            file_extension = Path(file.filename).suffix
            unique_filename = f"{file_id}{file_extension}"
            file_path = upload_dir / unique_filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            size = file_path.stat().st_size

            logger.info(f"Saved file to: {file_path} (size: {size} bytes)")

            orm = File(
                id=file_id,
                name=file.filename,
                size=size,
                content_type=file.content_type
            )

            session.add(orm)

            results.append(FileCreate(
                name=orm.name,
                size=orm.size,
                content_type=orm.content_type
            ))
        
        upload_task.delay(client_id, [file.model_dump() for file in results])

        return results