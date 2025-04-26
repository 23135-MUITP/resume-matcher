import streamlit as st
import PyPDF2
import docx
from sklearn.feature_extraction.text import CountVectorizer
import re

# Function to read a resume file
def read_resume(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text
        return text
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    else:
        return None

# Function to clean and extract keywords
def extract_keywords(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters
    words = text.split()
    return words

# Function to generate report
def generate_report(resume_words, jd_words):
    resume_set = set(resume_words)
    jd_set = set(jd_words)
    
    matched_keywords = resume_set.intersection(jd_set)
    missing_keywords = jd_set.difference(resume_set)
    
    score = (len(matched_keywords) / len(jd_set)) * 100 if jd_set else 0
    
    return score, matched_keywords, missing_keywords

# Streamlit App
st.set_page_config(page_title="Resume Matcher", layout="centered")

st.title("📄 Resume Matcher and Improvement Suggester")

st.write("Upload your resume and job description (JD) to see how well they match and get suggestions to improve your resume!")

# Upload Resume
resume_file = st.file_uploader("Upload your Resume (pdf, docx, txt)", type=["pdf", "docx", "txt"])

# Job Description Input
st.subheader("Job Description Input")
jd_option = st.radio("Choose JD input method:", ("Upload JD File", "Enter JD Text"))

jd_text = ""

if jd_option == "Upload JD File":
    jd_file = st.file_uploader("Upload JD (pdf, docx, txt)", type=["pdf", "docx", "txt"], key="jd_file")
    if jd_file is not None:
        jd_text = read_resume(jd_file)
else:
    jd_text = st.text_area("Paste the Job Description here")

# Match Button
if st.button("Match!"):
    if resume_file and jd_text:
        resume_text = read_resume(resume_file)
        if not resume_text:
            st.error("Unsupported Resume file type.")
        else:
            resume_words = extract_keywords(resume_text)
            jd_words = extract_keywords(jd_text)
            
            score, matched_keywords, missing_keywords = generate_report(resume_words, jd_words)
            
            st.success(f"✅ Matching Score: {score:.2f}%")
            
            with st.expander("🔍 Detailed Matching Report"):
                st.markdown("### 🟢 Keywords Present in Resume:")
                st.write(", ".join(matched_keywords) if matched_keywords else "No keywords matched.")

                st.markdown("### 🔴 Keywords Missing from Resume (Suggestions to add):")
                st.write(", ".join(missing_keywords) if missing_keywords else "Your resume covers all keywords! 🚀")
    else:
        st.error("Please upload both Resume and JD!")

