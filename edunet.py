import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import base64
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import numpy as np
import docx
import io
import zipfile
import json

# SEO Meta Tags
st.markdown("""
    <meta name="google-site-verification" content="Tg1j0KCe7DmFC15mUlV0N3BxjuCba7gHUeVmMHDg-yA" />
    <meta name="description" content="AI-powered resume screening and candidate ranking system. Upload resumes and job descriptions to automatically rank candidates based on relevance." />
    <meta name="keywords" content="resume screening, AI recruitment, candidate ranking, job matching, HR technology" />
    <meta name="robots" content="index, follow" />
    <meta property="og:title" content="HireVision AI - Resume Screening & Candidate Ranking" />
    <meta property="og:description" content="AI-powered resume screening and candidate ranking system for efficient recruitment." />
    <meta property="og:type" content="website" />
    <title>HireVision AI - Resume Screening & Candidate Ranking</title>
""", unsafe_allow_html=True)

# Structured Data for Search Engines
structured_data = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "HireVision AI",
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "Web",
    "description": "AI-powered resume screening and candidate ranking system for efficient recruitment.",
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
    }
}

st.markdown(f"""
    <script type="application/ld+json">
    {json.dumps(structured_data)}
    </script>
""", unsafe_allow_html=True)

def extract_text_from_pdf(file):
    try:
        pdf = PdfReader(file)
        return "".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        st.error(f"Error reading {file.name}: {e}")
        return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading {file.name}: {e}")
        return ""

def extract_text_from_txt(file):
    try:
        return file.getvalue().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading {file.name}: {e}")
        return ""

def extract_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    elif file.name.endswith(".txt"):
        return extract_text_from_txt(file)
    else:
        st.error(f"Unsupported file format: {file.name}")
        return ""

def rank_resumes(job_description, resumes, threshold):
    vectorizer = TfidfVectorizer()
    job_desc_vector = vectorizer.fit_transform([job_description])
    resume_vectors = vectorizer.transform(resumes)
    similarity_scores = cosine_similarity(job_desc_vector, resume_vectors).flatten()

    threshold_normalized = threshold / 100.0

    filtered_indices = np.where(similarity_scores >= threshold_normalized)[0]
    filtered_resumes = [resumes[i] for i in filtered_indices]
    filtered_scores = similarity_scores[filtered_indices]

    normalized_scores = filtered_scores * 100

    ranked_resumes = list(zip(filtered_indices, normalized_scores))
    ranked_resumes.sort(key=lambda x: x[1], reverse=True)

    scores = [score for _, score in ranked_resumes]
    original_indices = [index for index, _ in ranked_resumes]

    return scores, original_indices

def create_download_link(df, filename="results.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download CSV File</a>'

def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="viridis").generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

def highlight_words(resume_text, job_description):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
    feature_names = vectorizer.get_feature_names_out()
    word_scores = {word: tfidf_matrix[1, vectorizer.vocabulary_[word]] for word in feature_names}
    highlighted_text = "".join(
        f'<span style="background-color: {"green" if word.lower() in job_description.lower() else "yellow" if word_scores.get(word.lower(), 0) > 0.1 else "none"}; padding: 2px; border-radius: 3px;">{word}</span> '
        for word in resume_text.split()
    )
    return highlighted_text.strip()

def send_email(results, recipient_email, uploaded_files, top_n):
    try:
        sender_email = "prvenkat113@gmail.com"
        sender_password = "pbfv qafs vfwa tazo"
        subject = "RESUME SCORE REPORT FROM HIREVISIONAI"
        top_resumes = results.head(top_n)
        top_files = [file for file in uploaded_files if file.name in top_resumes["Resume"].values]
        body = f"""<h2>RESUME SCORE REPORT FROM HIREVISIONAI</h2><p>Here are the top {top_n} ranked resumes:</p>{top_resumes.to_html(index=False)}<p>Please find the top {top_n} resumes attached.</p>"""
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = sender_email, recipient_email, subject
        msg.attach(MIMEText(body, "html"))
        for file in top_files:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.getvalue())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={file.name}")
            msg.attach(part)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

def create_zip_download_link(files, filename="resumes.zip"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            zip_file.writestr(file.name, file.getvalue())
    b64 = base64.b64encode(zip_buffer.getvalue()).decode()
    return f'<a href="data:application/zip;base64,{b64}" download="{filename}">📥 Download {filename}</a>'

def main():
    st.title("🚀 AI Resume Screening & Candidate Ranking System")
    st.markdown("**Upload resumes and a job description to rank candidates based on relevance.**")
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = None

    with st.sidebar:
        st.header("⚙️ Options")
        threshold = st.slider("Set similarity threshold (0-100)", 0, 100, 30)
        top_n = st.number_input("Number of top resumes", min_value=1, value=5)

        st.markdown("""
        <style>
        .email-header {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .tooltip {
            cursor: pointer;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>
        <div class="email-header">
            <h3 style="margin: 0;">📧 Email Notifications</h3>
            <div class="tooltip">ℹ️
                <span class="tooltiptext">
                    When you click "Send Results via Email," the top N resumes will be sent to the specified email address as attachments.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        recipient_email = st.text_input("Enter recipient email")
        if st.button("Send Results via Email"):
            if "results" in st.session_state and st.session_state.uploaded_files:
                send_email(st.session_state.results, recipient_email, st.session_state.uploaded_files, top_n)
            else:
                st.warning("No results to send. Please upload resumes and rank them first.")
    st.header("📝 Job Description")
    job_description_option = st.radio("Input method:", ("Text Input", "Upload File"), key="job_desc_option")
    job_description = ""
    if job_description_option == "Text Input":
        job_description = st.text_area("Enter job description", height=200, key="job_desc_text")
    else:
        uploaded_jd_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"], key="jd_uploader")
        if uploaded_jd_file:
            job_description = extract_text(uploaded_jd_file)
    st.header("📂 Upload Resumes")
    uploaded_files = st.file_uploader("Upload Files", type=["pdf", "docx", "txt"], accept_multiple_files=True, key="resume_uploader")
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
    if uploaded_files and job_description:
        st.header("📊 Ranking Resumes")
        resumes = [extract_text(file) for file in uploaded_files]
        scores, original_indices = rank_resumes(job_description, resumes, threshold)
        if len(scores) > 0:
            filtered_uploaded_files = [uploaded_files[i] for i in original_indices]
            results = pd.DataFrame({"Resume": [file.name for file in filtered_uploaded_files], "Score": scores}).sort_values(by="Score", ascending=False)
            results["Rank"] = range(1, len(results) + 1)
            st.session_state.results = results
            st.subheader(f"🏆 Top {top_n} Resumes")
            for resume, score in zip(results["Resume"].head(top_n), results["Score"].head(top_n)):
                with st.expander(f"📄 {resume} (Score: {score:.2f})"):
                    resume_text = resumes[original_indices[list(results["Resume"]).index(resume)]]
                    st.markdown(highlight_words(resume_text, job_description), unsafe_allow_html=True)
            if len(results) > top_n:
                with st.expander(f"📋 Resumes After Top {top_n}"):
                    remaining_resumes = results.iloc[top_n:].reset_index(drop=True)
                    st.table(remaining_resumes[["Rank", "Resume", "Score"]])
            st.subheader("📊 Job Description Word Cloud")
            generate_wordcloud(job_description)
            st.subheader("📥 Download Results")
            st.markdown(create_download_link(results), unsafe_allow_html=True)

            # Download All Resumes Zip
            st.subheader("📥 Download All Resumes (ZIP)")
            st.markdown(create_zip_download_link(uploaded_files, "all_resumes.zip"), unsafe_allow_html=True)

            # Download Top N Resumes Zip
            top_files = [uploaded_files[original_indices[i]] for i in range(min(top_n, len(original_indices)))]
            st.subheader(f"📥 Download Top {top_n} Resumes (ZIP)")
            st.markdown(create_zip_download_link(top_files, f"top_{top_n}_resumes.zip"), unsafe_allow_html=True)
            #say that try our new feature sending to mail from the side bar
            st.markdown("Try our new feature in sidebar: Send Results via Email")
            st.markdown("**When you click 'Send Results via Email,' the top N resumes will be sent to the specified email address as attachments.**")
            

        else:
            st.warning("No resumes passed the similarity threshold.")

if __name__ == "__main__":
    main()