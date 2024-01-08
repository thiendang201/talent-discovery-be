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
from routers.resume.schemas import AwardRequest, CertificationRequest, EducationRequest, LanguageRequest, ProjectExperienceRequest, ReferencesRequest, ResumeData, ResumeRequest, SkilRequest, WorkExperienceRequest
from supabase_client.main import get_storage_bucket, supabase_client
from unstructured.partition.pdf import partition_pdf
from pdf2image import convert_from_bytes
from PIL.Image import Image

from exception import UnicornException
from supabase_client.table_names import * 
from sentence_transformers import SentenceTransformer


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


def extract_resume(resume_content: str) -> ResumeData:
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


def save_resume(request: ResumeRequest):
    data, count = supabase_client.table(RESUME_TABLE_NAME).insert(
        {
            "resume_thumbnail_url": request.resume_thumbnail_url,
            "resume_file_hash": request.resume_file_hash,
            "resume_file_path": request.resume_file_path,
            "folder_id": request.folder_id,
            "job_title": request.job_title,
            "job_title_embedding": request.job_title_embedding,
            "summary_or_objectives": request.summary_or_objectives,
            "full_name": request.full_name,
            "email": request.email,
            "phone_number": request.phone_number,
            "address": request.address,
            "tolal_years_experience": request.tolal_years_experience,
            "folder_id": request.folder_id
        }
    ).execute()
    return data[1][0]['resume_id']

def save_reference(request: ReferencesRequest):
    supabase_client.table(RESUME_REFERENCE_TABLE_NAME).insert(
        {
            "resume_id": request.resume_id,
            "reference_link": request.reference_link,
        }
    ).execute()

def save_award(request: AwardRequest):
    supabase_client.table(RESUME_AWARD_TABLE_NAME).insert(
        {
            "resume_id": request.resume_id,
            "title": request.title,
            "award_title_embedding": request.award_title_embedding,
            "date": request.date,
        }
    ).execute()

def save_certification(request: CertificationRequest):
    supabase_client.table(RESUME_CERTIFICATION_TABLE_NAME).insert(
        {
            "resume_id": request.resume_id,
            "title": request.title,
            "certification_embedding": request.certification_embedding,
            "date": request.date,
        }
    ).execute()

def save_education(request: EducationRequest):
    supabase_client.table(RESUME_EDUCATION_TABLE_NAME).insert(
        {
            "resume_id": request.resume_id,
            "name": request.name,
            "title": request.title,
            "education_title_embedding": request.education_title_embedding,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "gpa": request.gpa,
        }
    ).execute()

def save_language(request: LanguageRequest):
    supabase_client.table(RESUME_LANGUAGE_TABLE_NAME).insert(
        {
            "resume_id": request.resume_id,
            "language_name": request.language_name,
            "language_name_embedding": request.language_name_embedding
        }
    ).execute()

def save_project_experience(request: ProjectExperienceRequest):
    supabase_client.table(RESUME_PROJECT_EXPERIENCE_TABLE_NAME).insert(
        {
            "resume_id": request.resume_id,
            "project_name": request.project_name,
            "project_description": request.project_description,
            "project_technologies": request.project_technologies,
            "responsibilities": request.responsibilities,
            "repository_url": request.repository_url,
            "demo_or_live_url": request.demo_or_live_url,
            "start_date": request.start_date,
            "end_date": request.end_date,
        }
    ).execute()

def save_skill(request: SkilRequest):
    supabase_client.table(RESUME_SKILL_TABLE_NAME).insert(
        {
            "resume_id": request.resume_id,
            "skill_name": request.skill_name,
            "skill_name_embedding": request.skill_name_embedding
        }
    ).execute()

def save_work_experience(request: WorkExperienceRequest):
    supabase_client.table(RESUME_WORK_EXPERIENCE_TABLE_NAME).insert(
        {
            "resume_id": request.resume_id,
            "job_title": request.job_title,
            "job_sumary": request.job_sumary,
            "company_name": request.company_name,
            "start_date": request.start_date,
            "end_date": request.end_date,
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

def embedding(text: str):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embedding = model.encode(text)
    return embedding.tolist()