from datetime import date as Date
from typing import List
from pydantic import BaseModel


class BasicInfo(BaseModel):
    fullName: str
    email: str
    phoneNumber: str
    address: str | None = None
    linkedInMainPageUrl: str | None = None
    githubMainPageUrl: str | None = None
    portfolioMainPageUrl: str | None = None
    jobTitle: str | None = None
    summaryOrObjectives: str | None = None


class Award(BaseModel):
    title: str
    date: Date | None = None


class Certifications(BaseModel):
    title: str
    date: Date | None = None


class Educations(BaseModel):
    educationName: str
    startDate: Date | None = None
    endDate: Date | None = None
    major: str | None = None
    gpa: float | None = None


class WorkExperiences(BaseModel):
    companyName: str
    jobTitle: str | None = None
    jobSumary: str | None = None
    startDate: Date | None = None
    endDate: Date | None = None


class ProjectExperiences(BaseModel):
    projectName: str
    description: str | None = None
    technologies: str | None = None
    responsibilities: str | None = None
    startDate: Date
    endDate: Date | None = None
    repositoryUrl: str | None = None
    demoOrLiveUrl: str | None = None


class ResumeData(BaseModel):
    basicInfo: BasicInfo
    skills: List[str] | None = None
    languages: List[str] | None = None
    awards: List[Award] | None = None
    certifications: List[Certifications] | None = None
    educations: List[Educations] | None = None
    workExperiences: List[WorkExperiences] | None = None
    projectExperiences: List[ProjectExperiences] | None = None

class ResumeRequest(BaseModel):
    resume_thumbnail_url: str
    resume_file_hash: str
    resume_file_path: str
    folder_id: str
    job_title: str
    job_title_embedding: List[float]
    summary_or_objectives: str
    full_name: str
    email: str
    phone_number: str
    address: str
    tolal_years_experience: int

class ReferencesRequest(BaseModel):
    resume_id: str
    reference_link: str 

class AwardRequest(BaseModel):
    resume_id: str
    title: str
    award_title_embedding: List[float]
    date: str

class CertificationRequest(BaseModel):
    resume_id: str  
    title: str
    certification_embedding: List[float]
    date: str

class EducationRequest(BaseModel):
    resume_id: str
    name: str
    education_name_embedding: List[float]
    start_date: str
    end_date: str
    gpa: float

class LanguageRequest(BaseModel):
    resume_id: str
    language_name: str
    language_name_embedding: List[float]

class ProjectExperienceRequest(BaseModel):
    resume_id: str
    project_name: str
    project_description: str
    project_technologies: str
    responsibilities: str
    repository_url: str
    demo_or_live_url: str
    start_date: str
    end_date: str

class SkilRequest(BaseModel):
    resume_id: str
    skill_name: str
    skill_name_embedding: List[float]

class WorkExperienceRequest(BaseModel):
    resume_id: str
    job_title: str
    job_sumary: str
    company_name: str
    start_date: str
    end_date: str