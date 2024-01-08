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
