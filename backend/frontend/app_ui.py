import streamlit as st
import requests

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# ---------- Page Setup ----------
st.set_page_config(page_title="PatentAI", layout="wide")
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
        }
        .title-container {
            background-color: #003366;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
        }
        .title-container h1 {
            color: white;
            text-align: center;
            font-size: 2.5rem;
            margin: 0;
        }
        .summary-box {
            background-color: #e6f0ff;
            border: 1px solid #99ccff;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Demo Ideas ----------
demo_ideas = {
    "Smart Door Lock": {
        "title": "Smart Door Lock",
        "description": "A smart door lock that uses facial recognition and WiFi to grant access without keys."
    },
    "AI Medical Scanner": {
        "title": "AI Medical Scanner",
        "description": "A portable scanner that uses AI to diagnose skin conditions and send results to doctors remotely."
    },
    "Smart Recycling Bin": {
        "title": "Smart Recycling Bin",
        "description": "An intelligent bin that uses computer vision to sort waste and reward users with points."
    },
    "Child Safety Necklace": {
        "title": "Child Safety Necklace",
        "description": "A wearable GPS tracker for children with SOS alerts, live audio, and real-time location sharing."
    },
    "Self-Cleaning Solar Panels": {
        "title": "Self-Cleaning Solar Panels",
        "description": "Solar panels that use hydrophobic coating and vibration to remove dust without water or labor."
    }
}

# ---------- Sidebar ----------
st.sidebar.title("Demo Ideas")
selected_demo = st.sidebar.radio("Try a sample:", list(demo_ideas.keys()))

# Load selected demo
demo = demo_ideas[selected_demo]
default_title = demo["title"]
default_description = demo["description"]

# ---------- Header ----------
st.markdown('<div class="title-container"><h1>PatentAI</h1></div>', unsafe_allow_html=True)

with st.expander("About This Tool"):
    st.markdown("""
        PatentAI helps assess patent ideas using AI. It analyzes novelty, extracts keywords, and generates investor-ready pitches.
    """)

# ---------- Input Form ----------
with st.form("analyze_form"):
    st.subheader("Submit Your Invention")
    title = st.text_input("Title", value=default_title, key="title_input")
    description = st.text_area("Description", height=200, value=default_description, key="desc_input")
    submitted = st.form_submit_button("Run Full Analysis")

if submitted:
    if not title.strip() or not description.strip():
        st.warning("Both title and description are required.")
    else:
        with st.spinner("Analyzing with Groq AI..."):
            try:
                res = requests.post(f"{BACKEND_URL}/analyze", json={"title": title, "description": description})
                score_res = requests.post(f"{BACKEND_URL}/score", json={"description": description})
                keywords_res = requests.post(f"{BACKEND_URL}/keywords", json={"description": description})
                pitch_res = requests.post(f"{BACKEND_URL}/market-pitch", json={"description": description})

                if res.status_code == 200:
                    analysis = res.json().get("analysis", "")
                    novelty = score_res.json().get("novelty_score", "N/A")
                    keywords = keywords_res.json().get("keywords", "")
                    pitch = pitch_res.json().get("investor_pitch", "")

                    # ---------- Summary Card ----------
                    st.markdown("### Summary")
                    st.markdown(f"""
                        <div class="summary-box">
                            <strong>Title:</strong> {title} <br>
                            <strong>Novelty Score:</strong> {novelty.splitlines()[0] if novelty else "Pending"} <br>
                            <strong>Market Potential:</strong> {('Market' in analysis and analysis.split('Market')[1].split('Competitive')[0].strip()) if analysis else 'Pending'}
                        </div>
                    """, unsafe_allow_html=True)

                    # ---------- Result Tabs ----------
                    tabs = st.tabs(["Full Analysis", "Novelty Score", "Keywords", "Investor Pitch"])

                    with tabs[0]:
                        st.markdown("#### Technical & Market Analysis")
                        st.code(analysis, language="markdown")

                    with tabs[1]:
                        st.markdown("#### Novelty Score")
                        st.markdown(novelty)

                    with tabs[2]:
                        st.markdown("#### Extracted Keywords")
                        st.markdown(keywords)

                    with tabs[3]:
                        st.markdown("#### Pitch")
                        st.markdown(pitch)

                else:
                    st.error(f"API Error {res.status_code}: {res.text}")

            except Exception as e:
                st.error(f"Connection error: {str(e)}")
