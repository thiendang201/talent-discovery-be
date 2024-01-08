from typing import List
from fastapi import APIRouter, UploadFile, status
from exception import UnicornException
from openai_client.main import get_embedding
from tags import RESUME_TAG
from routers.resume.services import (
    calculate_hash,
    convert_img_to_bytes,
    extract_resume,
    find_resume_by_hash,
    generate_thumbnails,
    get_resume_content,
    save_resume,
    semantic_filter_resumes,
    upload_thumbnail,
    upload_resume_file,
    validate_file,
)


resumeRouter = APIRouter(prefix="/resume")


@resumeRouter.post("/upload", tags=[RESUME_TAG])
async def upload_resume(resume: UploadFile, fodler_id: str):
    isValid, error = validate_file(resume)

    if not isValid:
        raise error

    resume_bytes = await resume.read()
    resume_hash = calculate_hash(resume_bytes)
    duplicated_resume = find_resume_by_hash(resume_hash)

    if duplicated_resume:
        raise UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Resume file already exists",
            type="file.duplicated",
            data=duplicated_resume,
        )

    # process thumbnail
    thumbnails = generate_thumbnails(pdf=resume_bytes)
    thumbnail_bytes = convert_img_to_bytes(thumbnails[0])
    thumbnail_url = upload_thumbnail(thumbnail_bytes, fodler_id, resume_hash)

    # upload resume file
    resume_file_path = upload_resume_file(resume_bytes, fodler_id, resume_hash)

    # parse and save resume data
    resume_content = get_resume_content(resume.file)
    resume_data = extract_resume(resume_content)

    save_resume(
        resume_content=resume_content,
        resume_file_hash=resume_hash,
        resume_file_path=resume_file_path,
        resume_thumbnail_url=thumbnail_url,
        folder_id=fodler_id,
        job_title=resume_data.basicInfo.jobTitle,
        # job_title_embedding= resume_data.basicInfo.,
        # summary_or_objectives=str,
        # full_name=str,
        # emai=str,
        # phone_number=str,
        # address=str,
        # tolal_years_experience=int,
    )


# @resumeRouter.get("/filter", tags=[RESUME_TAG])
# async def filter_resumes(year_experiences: int, skills: str):
#     year_query = f"{year_experiences} years of experience"
#     year_query_embedding = get_embedding(year_query)
#     skill_query_embedding = get_embedding(skills)

#     return semantic_filter_resumes(skill_query_embedding)
