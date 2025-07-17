import streamlit as st
import requests

API_BASE_URL = "https://patentai-backend.onrender.com"

st.set_page_config(page_title="PatentAI", layout="wide")

st.title("PatentAI Interface")
st.markdown("Use the sidebar to choose a tool.")

# Sidebar for tool selection
tool = st.sidebar.selectbox("Choose a Tool", [
    "Invention Analyzer",
    "Novelty Score",
    "Keyword Extractor",
    "Market Pitch",
    "Health Check"
])

# Common input box
def get_description_input():
    return st.text_area("Enter your invention description", height=200)

# Invention Analyzer
if tool == "Invention Analyzer":
    st.header("Invention Analyzer")
    title = st.text_input("Title of your invention")
    description = get_description_input()
    if st.button("Analyze"):
        with st.spinner("Analyzing invention..."):
            res = requests.post(f"{API_BASE_URL}/analyze", json={
                "title": title,
                "description": description
            })
            if res.status_code == 200:
                st.success("Analysis Complete")
                st.markdown(res.json()["analysis"])
            else:
                st.error(res.json()["detail"])

# Novelty Score
elif tool == "Novelty Score":
    st.header("Novelty Scorer")
    description = get_description_input()
    if st.button("Score Novelty"):
        with st.spinner("Scoring..."):
            res = requests.post(f"{API_BASE_URL}/score", json={
                "description": description
            })
            if res.status_code == 200:
                st.success("Score Ready")
                st.markdown(res.json()["novelty_score"])
            else:
                st.error(res.json()["detail"])

# Keyword Extractor
elif tool == "Keyword Extractor":
    st.header("Technical Keyword Extractor")
    description = get_description_input()
    if st.button("Extract Keywords"):
        with st.spinner("Extracting..."):
            res = requests.post(f"{API_BASE_URL}/keywords", json={
                "description": description
            })
            if res.status_code == 200:
                st.success("Keywords Extracted")
                st.markdown(res.json()["keywords"])
            else:
                st.error(res.json()["detail"])

# Market Pitch
elif tool == "Market Pitch":
    st.header("Investor Pitch Generator")
    description = get_description_input()
    if st.button("Generate Pitch"):
        with st.spinner("Generating pitch..."):
            res = requests.post(f"{API_BASE_URL}/market-pitch", json={
                "description": description
            })
            if res.status_code == 200:
                st.success("Pitch Ready")
                st.markdown(res.json()["investor_pitch"])
            else:
                st.error(res.json()["detail"])

# Health Check
elif tool == "Health Check":
    st.header("API Health Check")
    if st.button("Run Health Check"):
        res = requests.get(f"{API_BASE_URL}/health")
        if res.status_code == 200:
            health_data = res.json()
            st.success("Service is Healthy")
            st.json(health_data)
        else:
            st.error("Health check failed")
