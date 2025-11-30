from fastapi import APIRouter, Depends, UploadFile
from typing import Annotated

from database import get_session
from models import FileCreate
from services.file import FileService
from worker import upload_task

router = APIRouter(
    prefix="/files"
)

@router.post("/upload/{client_id}", dependencies=[Depends(get_session)], response_model=list[FileCreate])
async def upload_files(client_id: str, files: list[UploadFile], file_service: Annotated[FileService, Depends()]) -> list[FileCreate]:
    results = await file_service.upload(client_id, files)
    upload_task.delay(client_id, [file.model_dump() for file in results])
    return results
