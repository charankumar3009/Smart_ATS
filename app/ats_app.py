import streamlit as st
import re
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


#Clean's the text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Extract's the text from the uploded pdf
def get_pdf_text(uploaded_file):

    try:
        text = extract_text(uploaded_file)
        return text
    except Exception as e:
        return ""
# Similarity percentage
def get_match_score(resume_text, job_description):
    # Clean's both texts
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(job_description)
    
    if not clean_resume or not clean_jd:
        return 0.0
    
    content = [clean_resume, clean_jd]
    cv = CountVectorizer()
    matrix = cv.fit_transform(content)
    similarity_matrix = cosine_similarity(matrix)
    return round(similarity_matrix[0][1] * 100, 2)
#Find's the missing words
def get_missing_keywords(resume_text, job_description):
    resume_words = set(clean_text(resume_text).split())
    jd_words = set(clean_text(job_description).split())
    
    missing = jd_words - resume_words
    
    stop_words = {
        'the', 'and', 'is', 'in', 'to', 'for', 'of', 'a', 'with', 'on', 'at', 
        'by', 'an', 'be', 'are', 'this', 'will', 'as', 'that', 'or', 'from',
        'can', 'have', 'has', 'but', 'not', 'we', 'you', 'your', 'our'
    }
    
    filtered_missing = [word for word in missing if word not in stop_words and len(word) > 2]
    
    return list(filtered_missing)

#  STREAMLIT UI

def main():
    st.set_page_config(page_title="Smart ATS", page_icon="🤖", layout="wide")
    
    st.title("🤖 Smart ATS: Resume Screener")
    st.markdown("### Optimize your resume for Applicant Tracking Systems")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Job Description")
        jd = st.text_area("Paste the Job Description (JD) here:", height=300)
        
    with col2:
        st.subheader("2. Your Resume")
        uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type="pdf")
    
    if st.button("Analyze Resume", type="primary"):
        if jd and uploaded_file:
            with st.spinner('Processing...'):
                # Extract the Text
                resume_text = get_pdf_text(uploaded_file)
                
                if resume_text:
                    # Calculate theScore
                    score = get_match_score(resume_text, jd)
                    st.divider()
                    st.subheader("Analysis Results")
                    
                    # Visual Score Meter
                    if score >= 60:
                        st.success(f" **Strong Match: {score}%**")
                        st.balloons()
                    elif score >= 40:
                        st.warning(f" **Average Match: {score}%**")
                    else:
                        st.error(f" **Low Match: {score}%**")
                        
                    st.progress(score / 100)
                    
                    # Missing Keywords Section
                    st.subheader("🔍 Missing Keywords")
                    st.write("These keywords appear in the JD but are missing from your resume:")
                    
                    missing_keywords = get_missing_keywords(resume_text, jd)
                    
                    if missing_keywords:
                        # Display's top 15 missing words 
                        st.write(", ".join(missing_keywords[:15]))
                        if len(missing_keywords) > 15:
                            st.caption(f"...and {len(missing_keywords) - 15} more.")
                        st.info("💡 **Tip:** Incorporate these words into your 'Skills' or 'Projects' section to improve your score.")
                    else:
                        st.success("🎉 Amazing! Your resume covers all the key terms found in the JD.")
                
                else:
                    st.error("Could not extract text from the PDF. Please ensure it is a text-based PDF, not an image scan.")
        else:
            st.warning("Please provide both a Job Description and a Resume PDF.")

if __name__ == "__main__":
    main()
