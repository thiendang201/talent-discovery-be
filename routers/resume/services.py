import hashlib
import io
from typing import BinaryIO, List
from fastapi import UploadFile, status
from constants import (
    MAX_SIZE_IN_MB,
    RESUMES_BUCKET,
    SUPPORTED_FILE_TYPES,
    THUMBNAILS_BUCKET,
)
from openai_client.main import parseResume
from routers.resume.schemas import ResumeData
from supabase_client.main import get_storage_bucket, supabase_client
from unstructured.partition.pdf import partition_pdf
from pdf2image import convert_from_bytes
from PIL.Image import Image

from exception import UnicornException
from supabase_client.table_names import RESUME_TABLE_NAME


def validate_file(file: UploadFile):
    if not file:
        return False, UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="No file found!",
            type="file.null",
        )

    if not 0 < file.size <= 1 * MAX_SIZE_IN_MB:
        return False, UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Supported file size is 0 - 5 MB",
            type="file.size.unsupported",
        )

    if not file.content_type in SUPPORTED_FILE_TYPES:
        return False, UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Unsupported file type: {file.content_type}. Supported types are {SUPPORTED_FILE_TYPES}",
            type="file.type.unsupported",
        )

    return True, None


def calculate_hash(file: bytes):
    md5 = hashlib.md5()
    md5.update(file)

    return md5.hexdigest()


def find_resume_by_hash(hash: str):
    res = (
        supabase_client.table(RESUME_TABLE_NAME)
        .select("*")
        .eq("resume_file_hash", hash)
        .maybe_single()
        .execute()
    )

    if res:
        return res.data

    return None


def get_resume_content(resume_file: BinaryIO):
    resume_elements = partition_pdf(file=resume_file)
    resume_content = "\n\n".join([str(el) for el in resume_elements])

    return resume_content


def extract_resume(resume_content: str):
    if not resume_content:
        raise UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="File content is empty",
            type="file.content.empty",
        )

    res = parseResume(resume_content)

    if res == "None":
        raise UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="File is not a resume",
            type="file.not.resume",
        )

    return ResumeData.model_validate_json(res)


def generate_thumbnails(pdf: bytes, firstPage=0, lastPage=1):
    return convert_from_bytes(pdf_file=pdf, first_page=firstPage, last_page=lastPage)


def convert_img_to_bytes(image: Image):
    image_BytesIO = io.BytesIO()
    image.save(image_BytesIO, format="PNG")

    return image_BytesIO.getvalue()


def upload_thumbnail(thumbnail: bytes, fodler_id: int, resume_file_hash: str):
    storage = get_storage_bucket(THUMBNAILS_BUCKET)
    thumbnail_path = f"folder_{fodler_id}/thumbnail_{resume_file_hash}.png"

    storage.upload(
        file=thumbnail, path=thumbnail_path, file_options={"content-type": "image/png"}
    )

    return storage.get_public_url(thumbnail_path)


def upload_resume_file(resume: bytes, fodler_id: int, resume_file_hash: str):
    storage = get_storage_bucket(RESUMES_BUCKET)
    file_path = f"folder_{fodler_id}/resume_{resume_file_hash}.pdf"

    storage.upload(
        file=resume,
        path=file_path,
        file_options={"content-type": "application/pdf"},
    )

    return file_path


def save_resume(
    resume_thumbnail_url: str,
    resume_file_hash: str,
    resume_file_path: str,
    resume_content: str,
    resume_embedding: List[float],
    folder_id: str,
    job_title: str,
    job_title_embedding: List[float],
    summary_or_objectives: str,
    full_name: str,
    emai: str,
    phone_number: str,
    address: str,
    tolal_years_experience: int,
):
    supabase_client.table(RESUME_TABLE_NAME).insert(
        {
            "resume_thumbnail_url": resume_thumbnail_url,
            "resume_file_hash": resume_file_hash,
            "resume_file_path": resume_file_path,
            "resume_content": resume_content,
            "resume_embedding": resume_embedding,
            "folder_id": folder_id,
            "job_title": job_title,
            "job_title_embedding": job_title_embedding,
            "summary_or_objectives": summary_or_objectives,
            "full_name": full_name,
            "emai": emai,
            "phone_number": phone_number,
            "address": address,
            "tolal_years_experience": tolal_years_experience,
        }
    ).execute()


def semantic_filter_resumes(year_query_embedding: List[float]):
    result = supabase_client.rpc(
        "match_resumes",
        {
            "query_embedding": year_query_embedding,
            "match_threshold": 0.75,
        },
    ).execute()

    print(result)

    return result
