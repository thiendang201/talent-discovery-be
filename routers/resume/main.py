import math
from typing import List
from fastapi import APIRouter, UploadFile, status
from fastapi.params import Depends
from pydantic import BaseModel
from exception import UnicornException
from openai_client.main import get_embedding
from routers.resume.schemas import (
    AwardRequest,
    KeywordType,
    ReferencesRequest,
    ResumeRequest,
    SearchResume,
)
from schemas import PageParams, PagedResponseSchema
from tags import RESUME_TAG
from routers.resume.services import *
import openai
from supabase_client.main import supabase_client
from sentence_transformers import SentenceTransformer, util
import torch
import ast
import json
import numpy as np
from configs import env_configs
from openai import OpenAI



apiKey = env_configs.get("OPENAI_API_KEY")
client = OpenAI(api_key=apiKey)


resumeRouter = APIRouter(prefix="/resume")


@resumeRouter.post("/upload", tags=[RESUME_TAG])
async def upload_resume(resume: UploadFile, folder_id: str):
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

    # parse and save resume data
    resume_content = get_resume_content(resume.file)
    resume_data = extract_resume(resume_content)

    print("resume_data", resume_data)

    # process thumbnail
    thumbnails = generate_thumbnails(pdf=resume_bytes)
    thumbnail_bytes = convert_img_to_bytes(thumbnails[0])
    thumbnail_url = upload_thumbnail(thumbnail_bytes, folder_id, resume_hash)

    # upload resume file
    resume_file_path = upload_resume_file(resume_bytes, folder_id, resume_hash)

    # save resume
    resume_request = ResumeRequest(
        resume_file_hash=resume_hash,
        resume_file_path=resume_file_path,
        resume_thumbnail_url=thumbnail_url,
        folder_id=folder_id,
        job_title=resume_data.basicInfo.jobTitle,
        job_title_embedding=embedding(resume_data.basicInfo.jobTitle),
        summary_or_objectives=resume_data.basicInfo.summaryOrObjectives,
        full_name=resume_data.basicInfo.fullName,
        email=resume_data.basicInfo.email,
        phone_number=resume_data.basicInfo.phoneNumber,
        address=resume_data.basicInfo.address,
        tolal_years_experience=0,
    )
    resume_id = save_resume(resume_request)

    # save reference
    if resume_data.basicInfo.linkedInMainPageUrl:
        reference_request = ReferencesRequest(
            resume_id=resume_id,
            reference_link=resume_data.basicInfo.linkedInMainPageUrl,
        )
        save_reference(reference_request)

    if resume_data.basicInfo.githubMainPageUrl:
        reference_request = ReferencesRequest(
            resume_id=resume_id, reference_link=resume_data.basicInfo.githubMainPageUrl
        )
        save_reference(reference_request)

    if resume_data.basicInfo.portfolioMainPageUrl:
        reference_request = ReferencesRequest(
            resume_id=resume_id,
            reference_link=resume_data.basicInfo.portfolioMainPageUrl,
        )
        save_reference(reference_request)

    # save award
    if resume_data.awards:
        for item in resume_data.awards:
            award_request = AwardRequest(
                resume_id=resume_id,
                title=item.title,
                award_title_embedding=embedding(item.title),
                date=item.date,
            )
            save_award(award_request)

    # save certifications
    if resume_data.certifications:
        for item in resume_data.certifications:
            certification_request = CertificationRequest(
                resume_id=resume_id,
                title=item.title,
                certification_embedding=embedding(item.title),
                date=item.date,
            )
            save_certification(certification_request)

    # save educations
    if resume_data.educations:
        for item in resume_data.educations:
            education_request = EducationRequest(
                resume_id=resume_id,
                name=item.educationName,
                education_name_embedding=embedding(item.educationName),
                start_date=item.startDate,
                end_date=item.endDate,
                gpa=item.gpa,
            )
            save_education(education_request)

    # save workExperiences
    if resume_data.workExperiences:
        for item in resume_data.workExperiences:
            workExperiences_request = WorkExperienceRequest(
                resume_id=resume_id,
                job_title=item.jobTitle,
                job_sumary=item.jobSumary,
                company_name=item.companyName,
                start_date=item.startDate,
                end_date=item.endDate,
            )
        save_work_experience(workExperiences_request)

    # save language
    if resume_data.languages:
        for item in resume_data.languages:
            language_request = LanguageRequest(
                resume_id=resume_id,
                language_name=item,
                language_name_embedding=embedding(item),
            )
            save_language(language_request)

    # save project experience
    if resume_data.projectExperiences:
        for item in resume_data.projectExperiences:
            projectExperiences_request = ProjectExperienceRequest(
                resume_id=resume_id,
                project_name=item.projectName,
                project_description=item.description,
                project_technologies=item.technologies,
                responsibilities=item.responsibilities,
                repository_url=item.repositoryUrl,
                demo_or_live_url=item.demoOrLiveUrl,
                start_date=item.startDate,
                end_date=item.endDate,
            )
            save_project_experience(projectExperiences_request)

    # save skill
    if resume_data.skills:
        for item in resume_data.skills:
            skill_request = SkilRequest(
                resume_id=resume_id,
                skill_name=item,
                skill_name_embedding=embedding(item),
            )
            save_skill(skill_request)


# @resumeRouter.get("/filter", tags=[RESUME_TAG])
# async def filter_resumes(year_experiences: int, skills: str):
#     year_query = f"{year_experiences} years of experience"
#     year_query_embedding = get_embedding(year_query)
#     skill_query_embedding = get_embedding(skills)

#     return semantic_filter_resumes(skill_query_embedding)


@resumeRouter.post("/search", tags=[RESUME_TAG])
def search_resumes(searchResume: SearchResume):
    query_embedding_job_title = embedding(searchResume.job_title)

    data, error = supabase_client.rpc(
        "match_jobtitles",
        {
            "query_embedding": query_embedding_job_title,
            "match_threshold": 0.64 if searchResume.job_title else 0,
            "id_folder": searchResume.folder_id,
        },
    ).execute()
    data_resumes = data[1]
    result_resume_search = []
    for resume in data_resumes:
        award_title_embedding = resume["award_title_embedding"]
        award_title_embedding = [
            ast.literal_eval(item) for item in award_title_embedding
        ]

        certification_embedding = resume["certification_embedding"]
        certification_embedding = [
            ast.literal_eval(item) for item in certification_embedding
        ]

        education_name_embedding = resume["education_name_embedding"]
        education_name_embedding = [
            ast.literal_eval(item) for item in education_name_embedding
        ]

        language_name_embedding = resume["language_name_embedding"]
        language_name_embedding = [
            ast.literal_eval(item) for item in language_name_embedding
        ]

        skill_name_embedding = resume["skill_name_embedding"]
        skill_name_embedding = [ast.literal_eval(item) for item in skill_name_embedding]

        search_awards = True
        for award in searchResume.awards:
            query_embedding_award = embedding(award.value)
            select_awards = util.semantic_search(
                np.array(query_embedding_award, dtype=np.float32),
                np.array(award_title_embedding, dtype=np.float32),
            )[0]
            select_awards = [item for item in select_awards if item["score"] >= 0.64]
            if len(select_awards) == 0 and award.required:
                search_awards = False
                break

        search_certifications = True
        for certification in searchResume.certificates:
            query_embedding_certification = embedding(certification.value)
            select_certifications = util.semantic_search(
                np.array(query_embedding_certification, dtype=np.float32),
                np.array(certification_embedding, dtype=np.float32),
            )[0]
            select_certifications = [
                item for item in select_certifications if item["score"] >= 0.64
            ]
            if len(select_certifications) == 0 and certification.required:
                search_certifications = False
                break

        search_languages = True
        for language in searchResume.languages:
            query_embedding_language = embedding(language.value)
            select_languages = util.semantic_search(
                np.array(query_embedding_language, dtype=np.float32),
                np.array(language_name_embedding, dtype=np.float32),
            )[0]
            select_languages = [
                item for item in select_languages if item["score"] >= 0.64
            ]
            if len(select_languages) == 0 and language.required:
                search_languages = False
                break

        search_educations = True
        for education in searchResume.educations:
            query_embedding_education = embedding(education.value)
            select_educations = util.semantic_search(
                np.array(query_embedding_education, dtype=np.float32),
                np.array(education_name_embedding, dtype=np.float32),
            )[0]
            select_educations = [
                item for item in select_educations if item["score"] >= 0.64
            ]
            if len(select_educations) == 0 and education.required:
                search_educations = False
                break

        search_skills = True
        for skill in searchResume.skills:
            query_embedding_skill = embedding(skill.value)
            select_skills = util.semantic_search(
                np.array(query_embedding_skill, dtype=np.float32),
                np.array(skill_name_embedding, dtype=np.float32),
            )[0]
            select_skills = [item for item in select_skills if item["score"] >= 0.64]
            if len(select_skills) == 0 and skill.required:
                search_skills = False
                break

        print(
            1111,
            search_awards,
            search_certifications,
            search_languages,
            search_educations,
            search_skills,
        )
        if (
            search_awards
            and search_certifications
            and search_languages
            and search_educations
            and search_skills
        ):
            result_resume_search.append(resume)
    return result_resume_search

@resumeRouter.post("/get_resume", tags=[RESUME_TAG])
def get_resume(resume_id: str):
    data, count = (
    supabase_client.table(RESUME_TABLE_NAME)
        .select("*", count="exact")
        .eq("resume_id", resume_id)
    ).execute()
    data_resume = data[1][0]

    storage = get_storage_bucket(RESUMES_BUCKET)
    resume_url = storage.create_signed_url(data_resume['resume_file_path'], 3600*24)['signedURL']
    return {
        'data': data_resume,
        'resume_url': resume_url
    }

@resumeRouter.get(
    "/keywords",
    tags=[RESUME_TAG],
)
async def get_keywords(
    keyword_type: KeywordType,
    search_value: str = "",
):
    data, count = (
        supabase_client.table("keywords")
        .select("keyword_id, keyword_value")
        .eq("keyword_type", keyword_type.value)
        .ilike('keyword_value', f"%{search_value}%")
    ).execute()

    # if search_value:
    #     data, count = (
    #         query
    #         .text_search("keyword_fts", f"`{search_value}` | ``")
    #     ).execute()
    # else:
    #     data, count = query.execute()
        

    results = data[1]

    return results
