from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from constants import RESUMES_BUCKET, THUMBNAILS_BUCKET
from schemas import PageParams, PagedResponseSchema
from supabase_client.main import get_storage_bucket, supabase_client
from supabase_client.table_names import FOLDER_TABLE_NAME
import math

from tags import FOLDER_TAG

from .schemas import NewFolderSchema, RemoveFolderSchema, UpdateFolderNameSchema


folderRouter = APIRouter(prefix="/folder")


@folderRouter.get(
    "/all",
    tags=[FOLDER_TAG],
)
async def get_folder_list(page_params: PageParams = Depends(), search_value: str = ""):
    start = (page_params.page - 1) * page_params.size
    end = start + page_params.size

    data, count = (
        supabase_client.table(FOLDER_TABLE_NAME)
        .select("*", count="exact")
        .ilike("folder_name", f"%{search_value}%")
        .range(start, end)
    ).execute()

    totalElements = count[1] or 0
    results = data[1]
    totalPages = math.ceil(totalElements / page_params.size)

    return PagedResponseSchema(
        page=page_params.page,
        size=page_params.size,
        totalElements=totalElements,
        totalPages=totalPages,
        results=results,
    )


@folderRouter.post("/create", tags=[FOLDER_TAG])
async def create_folder(folder: NewFolderSchema):
    current_user = supabase_client.auth.get_user().user
    supabase_client.table(FOLDER_TABLE_NAME).insert(
        {"user_id": current_user.id, "folder_name": folder.folder_name}
    ).execute()


@folderRouter.delete("/remove/{folder_id}", tags=[FOLDER_TAG])
async def removeFolder(folder_id: str):
    supabase_client.table(FOLDER_TABLE_NAME).delete().eq(
        "folder_id", folder_id
    ).execute()

    remove_folder_files(THUMBNAILS_BUCKET, folder_id)
    remove_folder_files(RESUMES_BUCKET, folder_id)


def remove_folder_files(bucket_name: str, folder_id: str):
    bucket = get_storage_bucket(bucket_name)
    folder_path = f"folder_{folder_id}"
    all_file_paths = [
        f"{folder_path}/{file['name']}" for file in bucket.list(folder_path)
    ]

    if len(all_file_paths) > 0:
        bucket.remove(all_file_paths)


@folderRouter.patch("/update", tags=[FOLDER_TAG])
async def updateFolder(folder: UpdateFolderNameSchema):
    supabase_client.table(FOLDER_TABLE_NAME).update(
        {"folder_name": folder.folder_name}
    ).eq("folder_id", folder.folder_id).execute()
