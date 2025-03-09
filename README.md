# 🤖 HireVisionAI  

HireVisionAI is a **Streamlit**-based AI-powered resume analysis tool that extracts text from PDF resumes and evaluates their similarity using **TF-IDF and cosine similarity**.  

## 🚀 Features  
- **Upload PDFs** and extract text from resumes  
- **Compute text similarity** between multiple resumes  
- **Visualize results** with similarity scores  
- **User-friendly interface** built with Streamlit  

## 🛠 Installation  

### 🔹 **Local Setup**  
1. **Clone the repository**  
   ```bash
   git clone https://github.com/Remo05102005/hirevisionai.git
   cd hirevisionai
Create a virtual environment (optional but recommended)
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
Run the Streamlit app
bash
Copy
Edit
streamlit run app.py
☁️ Deployment on Streamlit Cloud
Push your code to GitHub.
Go to Streamlit Cloud.
Click Deploy an app and connect your repository.
Ensure requirements.txt is present.
Click Deploy, and Streamlit will handle the rest!

📂 Project Structure
bash
Copy
Edit

📦 hirevisionai
│-- app.py                 # Main Streamlit application  
│-- requirements.txt        # Dependencies  
│-- README.md               # Documentation  
│-- data/                   # (Optional) Sample resumes for testing  

⚠️ Troubleshooting
ModuleNotFoundError: No module named 'PyPDF2' on Streamlit Cloud
Ensure PyPDF2 is in requirements.txt.
Restart the app via Manage App → Reboot & Clear Cache.

📌 Author
Developed by Revanth Venkat Pasupuleti

