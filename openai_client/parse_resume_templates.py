resumeTemplate1 = """
  basicInfo: 
    firstName
    lastName
    email
    phoneNumber
    address
    linkedInMainPageUrl
    githubMainPageUrl
    portfolioMainPageUrl
    jobTitle
    summaryOrObjectives
  skills  
  languages
  awards:
    title
    date
  cetifications:
    title
    date
  educations:
    educationName
    startDate
    endDate
    major
    gpa
  workExperiences
    companyName
    jobTitle
    jobSumary
    startDate
    endDate
  projectExperiences
    projectName
    description
    technologies
    responsibilities
    repositoryUrl
    demoOrLiveUrl
"""

resumeTemplate2 = """{{basic_info: {{first_name, last_name, email, phone_number, address, linkedin_url, github_main_page_url, portfolio_website_url, university, graduation_year, graduation_month, major, GPA}}, job_title, summaryOrObjectives: string, skills: string[], certifications: string[], languages: string[], work_experience: [{{job_title, company, location, duration, job_summary}}] or [], project_experience:[{{project_name, project_description, technologies, responsibilities, github_link}}]}}"""

resumeTemplate3 = """
  {
    basicInfo: {
      fullName: string
      email: string
      phoneNumber: string
      address: string
      linkedInMainPageUrl?: string | null
      githubMainPageUrl?: string | null
      portfolioMainPageUrl: string | null
      jobTitle: string
      summaryOrObjectives: string
    }
    skills: string[] | null
    languages: string[] | null
    awards: {
      title: string
      date: string (full ISO 8601 Formats) | null
    }[] | null
    certifications: {
      title: string
      date: string (full ISO 8601 Formats) | null
    }[] | null
    educations: {
      educationName: string
      startDate: string (full ISO 8601 Formats)
      endDate: string (full ISO 8601 Formats) | null
      major: string
      gpa: number
    }[] | null
    workExperiences: {
      companyName: string
      jobTitle: string
      jobSumary: string
      startDate: string (full ISO 8601 Formats)
      endDate: string (full ISO 8601 Formats) | null
    }[] | null
    projectExperiences: {
      projectName: string
      description: string
      technologies: string
      responsibilities: string
      startDate: string (full ISO 8601 Formats)
      endDate: string (full ISO 8601 Formats) | null
      repositoryUrl: string | null
      demoOrLiveUrl: string | null
    }[] | null
  }
"""
