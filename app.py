import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="JEE War Room", page_icon="🔥", layout="wide")

# --- DATA PERSISTENCE ---
if "syllabus" not in st.session_state:
    st.session_state.syllabus = {
        "Physics": {
            "chapters": ["Current Electricity ⬇", "Electrostatics ⬆", "Ray Optics ⬆⬆", "Magnetic Effects of Current", "Thermodynamics ⬆", "Dual Nature of Matter", "Atomic Physics ⬇", "Rotational Motion ⬆⬆", "Gravitation ⬇⬇", "Mechanical Properties of Fluids", "Semiconductors", "Work Power Energy", "Units and Dimensions ⬆", "Wave Optics", "Laws of Motion ⬇⬇", "Motion In One Dimension⬇", "Alternating Current ⬇⬇", "Capacitance", "Electromagnetic Induction ⬇⬇", "Nuclear Physics ⬇", "Kinetic Theory of Gases ⬇", "Oscillations", "Electromagnetic Waves", "Motion In Two Dimensions ⬇", "Mechanical Properties of Solids", "Waves and Sound", "Mathematics in Physics", "Center of Mass Momentum", "Thermal Properties of Matter", "Magnetic Properties of Matter", "Experimental Physics"],
            "data": {} 
        },
        "Chemistry": {
            "chapters": ["General Organic Chemistry ⬇", "Coordination Compounds", "Chemical Bonding", "d and f Block Elements", "Thermodynamics (C) ⬆", "Electrochemistry", "Structure of Atom", "Solutions", "Hydrocarbons", "Amines", "p Block Elements ⬇", "Chemical Kinetics ⬆", "Biomolecules", "Mole Concept ⬆", "Aldehydes and Ketones", "Periodic Table ⬆", "Haloalkanes and Haloarenes ⬇", "Alcohols Phenols and Ethers ⬇", "Ionic Equilibrium ⬆", "Redox Reactions ⬇", "Chemical Equilibrium", "Practical Chemistry", "Carboxylic Acid Derivatives"],
            "data": {}
        },
        "Maths": {
            "chapters": ["Three-Dimensional Geometry ⬇", "Sequences and Series ⬇", "Matrices Determinants ⬇", "Vector Algebra ⬇", "Definite Integration", "Functions", "Binomial Theorem", "Differential Equations", "Probability", "Permutation Combination", "Straight Lines ⬆", "Area Under Curves", "Complex Number", "Application of Derivatives ⬇", "Sets and Relations", "Quadratic Equation", "Circle ⬇", "Statistics ⬇", "Limits", "Parabola ⬆", "Hyperbola", "Continuity and Differentiability", "Ellipse ⬆", "Inverse Trigonometric Functions", "Indefinite Integration", "Trigonometric Equations", "Differentiation", "Trigonometric Ratios & Identities", "Basic of Mathematics"],
            "data": {}
        }
    }
    # Initialize checkbox states
    for subj in st.session_state.syllabus:
        for chap in st.session_state.syllabus[subj]["chapters"]:
            st.session_state.syllabus[subj]["data"][chap] = {
                "Theory": False, "Rev": False, "PYQ23": False, "PYQ24": False, "PYQ25": False
            }

if "tasks" not in st.session_state:
    st.session_state.tasks = {"Daily": [], "Weekly": []}

if "scores" not in st.session_state:
    st.session_state.scores = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Command Center")
    
    # API KEY HANDLING
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        st.success("✅ AI Connected")
        ai_available = True
    except Exception:
        st.error("⚠️ Waiting for API Key in Secrets")
        ai_available = False

    st.divider()
    
    # SAVE/LOAD Logic
    st.write("💾 **Save Data (Daily)**")
    json_data = json.dumps({
        "syllabus": st.session_state.syllabus,
        "tasks": st.session_state.tasks,
        "scores": st.session_state.scores
    })
    st.download_button("Download Progress", json_data, file_name="jee_data.json", mime="application/json")

    uploaded_file = st.file_uploader("Restore Progress", type="json")
    if uploaded_file is not None:
        try:
            loaded_data = json.load(uploaded_file)
            st.session_state.syllabus = loaded_data["syllabus"]
            st.session_state.tasks = loaded_data["tasks"]
            st.session_state.scores = loaded_data["scores"]
            st.success("Restored!")
            st.rerun()
        except:
            pass

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📚 Syllabus", "🎯 Goals", "📊 Scores", "🧘 Focus"])

# --- TAB 1: SYLLABUS ---
with tab1:
    view_mode = st.radio("View Mode", ["Horizontal", "Vertical"], horizontal=True)
    
    subjects = ["Physics", "Chemistry", "Maths"]
    cols = st.columns(3) if view_mode == "Horizontal" else [st.container(), st.container(), st.container()]
    
    for i, subj in enumerate(subjects):
        color_map = {"Physics": "blue", "Chemistry": "orange", "Maths": "#00E5FF"}
        with cols[i]:
            st.markdown(f"<h3 style='color: {color_map[subj]};'>{subj}</h3>", unsafe_allow_html=True)
            
            # Headers
            h_cols = st.columns([3, 1, 1, 1, 1, 1])
            h_cols[0].caption("Chapter")
            h_cols[1].caption("T")
            h_cols[2].caption("R")
            h_cols[3].caption("23")
            h_cols[4].caption("24")
            h_cols[5].caption("25")
            
            for chap in st.session_state.syllabus[subj]["chapters"]:
                c_cols = st.columns([3, 1, 1, 1, 1, 1])
                c_cols[0].write(f"**{chap}**")
                data = st.session_state.syllabus[subj]["data"][chap]
                data["Theory"] = c_cols[1].checkbox("", value=data["Theory"], key=f"{subj}{chap}T")
                data["Rev"] = c_cols[2].checkbox("", value=data["Rev"], key=f"{subj}{chap}R")
                data["PYQ23"] = c_cols[3].checkbox("", value=data["PYQ23"], key=f"{subj}{chap}23")
                data["PYQ24"] = c_cols[4].checkbox("", value=data["PYQ24"], key=f"{subj}{chap}24")
                data["PYQ25"] = c_cols[5].checkbox("", value=data["PYQ25"], key=f"{subj}{chap}25")
            st.divider()

# --- TAB 2: GOALS ---
with tab2:
    layout = st.radio("Layout", ["Side-by-Side", "Stacked"], horizontal=True)
    cd, cw = st.columns(2) if layout == "Side-by-Side" else (st.container(), st.container())

    def task_list(name, key):
        st.subheader(name)
        new_t = st.text_input(f"Add {name}", key=f"in_{key}")
        if st.button(f"Add", key=f"btn_{key}") and new_t:
            st.session_state.tasks[key].append({"txt": new_t, "date": str(datetime.now()), "done": False})
            st.rerun()
        
        for idx, t in enumerate(st.session_state.tasks[key]):
            c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
            done = c1.checkbox("", t["done"], key=f"{key}{idx}")
            
            # Red Alert
            dt = datetime.strptime(t["date"], "%Y-%m-%d %H:%M:%S.%f")
            is_late = (datetime.now() - dt > timedelta(hours=24)) if key == "Daily" else (datetime.now() - dt > timedelta(days=7))
            
            style = "color:red" if is_late and not done else ""
            txt = f"~~{t['txt']}~~" if done else t['txt']
            c2.markdown(f"<span style='{style}'>{txt}</span>", unsafe_allow_html=True)
            
            if c3.button("X", key=f"d_{key}{idx}"):
                st.session_state.tasks[key].pop(idx)
                st.rerun()
            st.session_state.tasks[key][idx]["done"] = done

    with cd: task_list("Daily Targets", "Daily")
    with cw: task_list("Weekly Goals", "Weekly")

# --- TAB 3: SCORES ---
with tab3:
    c1, c2, c3, c4, c5 = st.columns([2,1,1,1,1])
    name = c1.text_input("Test Name")
    p = c2.number_input("P", 0, 100)
    c = c3.number_input("C", 0, 100)
    m = c4.number_input("M", 0, 100)
    if c5.button("Save"):
        st.session_state.scores.append({"Test": name, "P": p, "C": c, "M": m, "Total": p+c+m})
        st.rerun()
    
    if st.session_state.scores:
        df = pd.DataFrame(st.session_state.scores)
        st.dataframe(df, use_container_width=True)
        st.metric("Avg Total", f"{df['Total'].mean():.1f}")

# --- TAB 4: FOCUS (AI) ---
# --- TAB 4: FOCUS (AI) ---
with tab4:
    st.subheader("🧠 AI Question Bank")
    
    # Debugging: Print the key status (First 4 chars only to keep it safe)
    if "GEMINI_API_KEY" in st.secrets:
        masked_key = st.secrets["GEMINI_API_KEY"][:4] + "..."
        st.caption(f"Debug: Key loaded starting with {masked_key}")
    
    if st.button("Ask Gemini AI"):
        if ai_available:
            try:
                # Try the Flash model first
                model = genai.GenerativeModel('gemini-1.5-flash')
                resp = model.generate_content("Give me 1 hard JEE Mains Physics question (Topic: Mechanics). Just the question.")
                
                st.info(resp.text)
                with st.expander("Show Answer"):
                    resp2 = model.generate_content(f"What is the answer to: {resp.text}")
                    st.write(resp2.text)
            except Exception as e:
                # THIS WILL SHOW THE REAL ERROR
                st.error(f"Detailed Error: {e}")
        else:
            st.warning("Connect API Key first")


