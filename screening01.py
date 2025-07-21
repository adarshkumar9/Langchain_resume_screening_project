from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Load the API Key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Gemini model via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  
    temperature=0.3
)
########################
from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_template("""
You are a resume screening assistant.

Given the following Job Description (JD), extract 5 relevant screening questions that would help evaluate a candidate. Also mention the expected answer format (e.g., Yes/No, Rating, Short Text).

JD:
{jd}
""")
#put JD here
jd_text = """Sample software developer job description 
At [Company X], software developers create programs that enrich lives. We hire 
people who are hungry for innovation and motivated to overcome challenges and 
setbacks. We’re looking for a software developer who displays enthusiastic 
leadership, and whose technical expertise allows them to seamlessly manage projects 
and prioritize deadlines. 
Objectives of this role 
 Build client-focused, next-generation web applications 
 Support full-stack web development by applying agile methodologies for 
sprint planning, design sessions, development, testing, and deployment 
 Oversee diverse, cohesive teams for high-quality delivery to clients 
 Design, develop, test, and enhance software solutions 
Responsibilities 
 Participate in the full software development lifecycle, including analysis, 
design, test, and delivery 
 Develop web applications using a variety of languages and technologies 
 Facilitate design and architecture brainstorms 
 Participate in code reviews 
 Collaborate with team members to define and implement solutions 
Required skills and qualifications 
 One or more years of experience in software development 
 Strong proficiency with JavaScript  
 Deep knowledge of programming languages such as Java, C/C++, Python, 
and Go 
Preferred skills and qualifications 
 Experience in developing software with HTML5 and CSS3 web standards 
 Familiarity with Angular, Polymer, Closure Library, or Backbone 
 Understanding of full-stack web, including protocols and web server 
optimization standards """
chain = prompt | llm

extracted_questions = chain.invoke({"jd": jd_text})
print(extracted_questions.content)
####################

# NEW: Google Drive API setup and fetch 5 resumes

from google.oauth2 import service_account  # 🔄 UPDATED (modern import)
from googleapiclient.discovery import build
from PyPDF2 import PdfReader

FOLDER_ID = "12wnBKp3bkc7V1czpLKvArUF1-HzZvL5E"


# Authorize Drive API
creds = service_account.Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

# Fetch 5 resume files from folder
results = drive_service.files().list(
    q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf'",
    fields="files(id, name)",
    pageSize=5  # LIMIT to 5 resumes only
).execute()

files = results.get("files", [])
print(f"Found {len(files)} PDF resumes in the folder.")
for f in files:
    print(f"File: {f['name']} (ID: {f['id']})")
###########

matching_prompt = PromptTemplate.from_template("""
You are an AI resume screener.

Given the following resume and a list of questions from a job description, identify whether each question is answered in the resume. Respond with Yes/No for each question.

Resume:
{resume}

Questions:
{questions}
""")
# New helper function to extract text from PDF on Google Drive
def extract_resume_text_from_drive(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    from io import BytesIO
    from googleapiclient.http import MediaIoBaseDownload

    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    reader = PdfReader(fh)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
############

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_to_sheet(name, results):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "service_account.json", scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("Resume Screening Results(langchain)").sheet1
    # Clean result lines and write in single row
    cleaned_results = [line.strip() for line in match_result.content.strip().split("\n") if line.strip()]
    sheet.append_row([file["name"]] + cleaned_results)


# Final Loop to Process Each Resume

for file in files:
    resume_text = extract_resume_text_from_drive(file["id"])
    match_chain = matching_prompt | llm
    match_result = match_chain.invoke({
        "resume": resume_text,
        "questions": extracted_questions.content
    })
    print(f"✅ Processed: {file['name']}")
    print(match_result.content)
    write_to_sheet(file["name"], match_result.content.split("\n"))
