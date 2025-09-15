# AI Resume Screening Pipeline

This project automates **resume screening** by combining **Google Gemini (via LangChain)**, **Google Drive**, and **Google Sheets**.  
It extracts job-specific screening questions from a Job Description (JD), evaluates resumes stored in a Google Drive folder, and saves structured results to a Google Sheet.

---

## 🚀 Features
- **LLM-powered JD analysis** → generates 5 key screening questions with expected answer formats.  
- **Resume ingestion from Google Drive** → fetches up to 5 resumes (PDF).  
- **LLM-based resume evaluation** → checks if resumes answer the generated questions.  
- **Results export to Google Sheets** → stores screening decisions in a structured format.  

---

## 🛠️ Tech Stack
- **Python 3.10+**
- **LangChain + Gemini API**
- **Google Drive API** (resume input)
- **PyPDF2** (resume text extraction)
- **Google Sheets API (gspread)** (results output)

---

## 📂 Project Structure
