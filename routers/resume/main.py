from typing import List
from fastapi import APIRouter, UploadFile, status
from exception import UnicornException
from openai_client.main import get_embedding
from routers.resume.schemas import AwardRequest, ReferencesRequest, ResumeRequest
from tags import RESUME_TAG
from routers.resume.services import *


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

    # save resume
    resume_request = ResumeRequest(
        resume_content = resume_content,
        resume_file_hash = resume_hash,
        resume_file_path = resume_file_path,
        resume_thumbnail_url = thumbnail_url,
        folder_id = fodler_id,
        job_title = resume_data.basicInfo.jobTitle,
        job_title_embedding =  embedding(resume_data.basicInfo.jobTitle),
        summary_or_objectives = resume_data.basicInfo.summaryOrObjectives,
        full_name = resume_data.basicInfo.fullName,
        emai = resume_data.basicInfo.email,
        phone_number = resume_data.basicInfo.phoneNumber,
        address = resume_data.basicInfo.address
    )
    resume_id = save_resume(resume_request)

    # save reference
    if resume_data.basicInfo.linkedInMainPageUrl:
        reference_request = ReferencesRequest(
            resume_id=resume_id,
            reference_link = resume_data.basicInfo.linkedInMainPageUrl
        )
        save_reference(reference_request)
    
    if resume_data.basicInfo.githubMainPageUrl:
        reference_request = ReferencesRequest(
            resume_id=resume_id,
            reference_link = resume_data.basicInfo.githubMainPageUrl
        )
        save_reference(reference_request)
    
    if resume_data.basicInfo.portfolioMainPageUrl:
        reference_request = ReferencesRequest(
            resume_id=resume_id,
            reference_link = resume_data.basicInfo.portfolioMainPageUrl
        )
        save_reference(reference_request)

    # save award
    if resume_data.awards:
        for item in resume_data.awards:
            award_request = AwardRequest(
                resume_id = resume_id,
                title = item.title,
                award_title_embedding = embedding(item.title),
                date = item.date,
            )
            save_award(award_request)

    # save certifications
    if resume_data.certifications:
        for item in resume_data.certifications:
            certification_request = CertificationRequest(
                resume_id = resume_id,
                title = item.title,
                certification_embedding = embedding(item.title),
                date = item.date
            )
            save_certification(certification_request)
    
    # save educations
    if resume_data.educations:
        for item in resume_data.educations:
            education_request = EducationRequest(
                resume_id = resume_id,
                name = item.educationName,
                education_name_embedding = embedding(item.educationName),
                start_date = item.startDate,
                end_date = item.endDate,
                gpa = item.gpa
            )
            save_education(education_request)
        
    # save workExperiences
    if resume_data.workExperiences:
        for item in resume_data.workExperiences:
            workExperiences_request = WorkExperienceRequest(
                resume_id = resume_id,
                job_title = item.jobTitle,
                job_sumary = item.jobSumary,
                company_name = item.companyName,
                start_date = item.startDate,
                end_date = item.endDate,
            )
        save_work_experience(workExperiences_request)

    # save language
    if resume_data.languages:
        for item in resume_data.languages:
            language_request = LanguageRequest(
                resume_id = resume_id,
                language_name = item,
                language_name_embedding = embedding(item)
            )
            save_language(language_request)

    # save project experience
    if resume_data.projectExperiences:
        for item in resume_data.projectExperiences:
            projectExperiences_request = ProjectExperienceRequest(
                resume_id = resume_id,
                project_name = item.projectName,
                project_description = item.description,
                project_technologies = item.technologies,
                responsibilities = item.responsibilities,
                repository_url = item.repositoryUrl,
                demo_or_live_url = item.demoOrLiveUrl,
                start_date = item.startDate,
                end_date = item.endDate,
            )
            save_project_experience(projectExperiences_request)
        
    # save skill
    if resume_data.skills:
        for item in resume_data.skills:
            skill_request = SkilRequest(
                resume_id = resume_id,
                skill_name = item,
                skill_name_embedding = embedding(item),
            )
            save_skill(skill_request)


    



# @resumeRouter.get("/filter", tags=[RESUME_TAG])
# async def filter_resumes(year_experiences: int, skills: str):
#     year_query = f"{year_experiences} years of experience"
#     year_query_embedding = get_embedding(year_query)
#     skill_query_embedding = get_embedding(skills)

#     return semantic_filter_resumes(skill_query_embedding)
