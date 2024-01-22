from datetime import date as Date
from enum import Enum
from typing import List
from pydantic import BaseModel


class BasicInfo(BaseModel):
    fullName: str | None = None
    email: str | None = None
    phoneNumber: str | None = None
    address: str | None = None
    linkedInMainPageUrl: str | None = None
    githubMainPageUrl: str | None = None
    portfolioMainPageUrl: str | None = None
    jobTitle: str | None = None
    summaryOrObjectives: str | None = None


class Award(BaseModel):
    title: str | None = None
    date: str | None = None


class Certifications(BaseModel):
    title: str | None = None
    date: str | None = None


class Educations(BaseModel):
    educationName: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    major: str | None = None
    gpa: float | None = None


class WorkExperiences(BaseModel):
    companyName: str | None = None
    jobTitle: str | None = None
    jobSumary: str | None = None
    startDate: str | None = None
    endDate: str | None = None


class ProjectExperiences(BaseModel):
    projectName: str | None = None
    description: str | None = None
    technologies: str | None = None
    responsibilities: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    repositoryUrl: str | None = None
    demoOrLiveUrl: str | None = None


class ResumeData(BaseModel):
    basicInfo: BasicInfo | None = None
    skills: List[str] | None = None
    languages: List[str] | None = None
    awards: List[Award] | None = None
    certifications: List[Certifications] | None = None
    educations: List[Educations] | None = None
    workExperiences: List[WorkExperiences] | None = None
    projectExperiences: List[ProjectExperiences] | None = None


class ResumeRequest(BaseModel):
    resume_thumbnail_url: str | None = None
    resume_file_hash: str | None = None
    resume_file_path: str | None = None
    folder_id: str | None = None
    job_title: str | None = None
    job_title_embedding: List[float]
    summary_or_objectives: str | None = None
    full_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    address: str | None = None
    tolal_years_experience: int


class ReferencesRequest(BaseModel):
    resume_id: str | None = None
    reference_link: str | None = None


class AwardRequest(BaseModel):
    resume_id: str | None = None
    title: str | None = None
    award_title_embedding: List[float]
    date: str | None = None


class CertificationRequest(BaseModel):
    resume_id: str | None = None
    title: str | None = None
    certification_embedding: List[float]
    date: str | None = None


class EducationRequest(BaseModel):
    resume_id: str | None = None
    name: str | None = None
    education_name_embedding: List[float]
    start_date: str | None = None
    end_date: str | None = None
    gpa: float | None = None


class LanguageRequest(BaseModel):
    resume_id: str | None = None
    language_name: str | None = None
    language_name_embedding: List[float]


class ProjectExperienceRequest(BaseModel):
    resume_id: str | None = None
    project_name: str | None = None
    project_description: str | None = None
    project_technologies: str | None = None
    responsibilities: str | None = None
    repository_url: str | None = None
    demo_or_live_url: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class SkilRequest(BaseModel):
    resume_id: str | None = None
    skill_name: str | None = None
    skill_name_embedding: List[float]


class WorkExperienceRequest(BaseModel):
    resume_id: str | None = None
    job_title: str | None = None
    job_sumary: str | None = None
    company_name: str | None = None
    start_date: str | None = None
    end_date: str | None = None

class KeywordType(str, Enum):
    JOB_TITLE = 'job_title',
    SKILL = 'skill',
    LANGUAGE = 'language',
    AWARD = 'award',
    CERTIFICATION = 'certification',
    EDUCATION = 'education'

class KeywordOption(BaseModel):
    value: str
    required: bool

class SearchResume(BaseModel):
    folder_id: str
    job_title: str
    awards: List[KeywordOption]
    certificates: List[KeywordOption]
    educations: List[KeywordOption]
    languages: List[KeywordOption]
    skills: List[KeywordOption]