import streamlit as st
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
from agents import FarmSupervisor
from storage import save_assessment, recent_assessments
from weather import fetch_weather

load_dotenv()
st.set_page_config(page_title="AgriPilot | Farm Intelligence", page_icon="🌱", layout="wide")

st.markdown("""
<style>
.main {background:#f7faf5}
[data-testid="stSidebar"] {background:#eef5e9}
.hero {padding:1.25rem 1.5rem;border-radius:16px;background:linear-gradient(110deg,#174d32,#3c8150);color:white}
.hero h1 {color:white;margin:0}.hero p {color:#e9f5e9;margin:.35rem 0 0}
.small-muted {color:#647568;font-size:.9rem}
div.stButton>button {background:#236b42;color:white;border-radius:9px;border:0}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🌱 AgriPilot</h1><p>Agentic farm decision support — weather-aware irrigation, soil guidance and crop-health triage.</p></div>', unsafe_allow_html=True)
st.write("")
with st.sidebar:
    st.header("Farm profile")
    farm_name=st.text_input("Farm / farmer name", "My Farm")
    crop=st.selectbox("Current crop", ["Paddy (rice)","Maize","Groundnut","Cotton","Chilli","Tomato","Banana","Other"])
    crop_stage=st.selectbox("Crop growth stage", ["Sowing / transplanting","Vegetative","Flowering","Fruiting / grain filling","Maturity / harvest"])
    area=st.number_input("Farm area (acres)", min_value=0.1, max_value=10000.0, value=2.0, step=0.1)
    st.caption("Location is used only to retrieve public forecast data.")
    lat=st.number_input("Latitude", min_value=-90.0,max_value=90.0,value=16.5449,format="%.4f")
    lon=st.number_input("Longitude", min_value=-180.0,max_value=180.0,value=81.5212,format="%.4f")
    st.caption("Default coordinates are approximate for Bhimavaram. Replace with your field location.")

left,right=st.columns([1.1,0.9],gap="large")
with left:
    st.subheader("1. Field observations")
    soil_type=st.selectbox("Soil type",["Clay","Sandy","Loamy","Black cotton","Red soil","Not sure"])
    soil_ph=st.number_input("Soil pH (if tested)",min_value=0.0,max_value=14.0,value=7.0,step=0.1)
    moisture=st.select_slider("Current soil moisture (your observation)",options=["Very dry","Dry","Moderate","Moist","Waterlogged"],value="Moderate")
    rainfall=st.number_input("Rainfall in last 24 hours (mm)",min_value=0.0,max_value=500.0,value=0.0,step=1.0)
    symptoms=st.multiselect("Visible crop symptoms",["Yellowing leaves","Brown / black spots","Leaf curling","Wilting","Stunted growth","White powder / fungal growth","Chewed leaves / holes","No visible symptoms"])
    notes=st.text_area("Additional observations",placeholder="When did symptoms start? Which leaves are affected? Any recent spray or fertilizer?")
    uploaded=st.file_uploader("Upload a crop photo (optional)",type=["jpg","jpeg","png"])
with right:
    st.subheader("2. Soil test (optional)")
    n=st.selectbox("Nitrogen status",["Unknown","Low","Medium","High"])
    p=st.selectbox("Phosphorus status",["Unknown","Low","Medium","High"])
    k=st.selectbox("Potassium status",["Unknown","Low","Medium","High"])
    st.info("For fertilizer decisions, use a recent soil-test report. The app will not invent fertilizer quantities.")
    st.subheader("3. Advisory settings")
    irrigation_method=st.selectbox("Irrigation method",["Flood / basin","Drip","Sprinkler","Furrow","Rain-fed"])
    water_available=st.selectbox("Water availability",["Limited","Moderate","Adequate"])
    advisory_level=st.selectbox("Advice preference",["Conservative (safety first)","Balanced"])

if st.button("🤖 Analyse farm & generate action plan", type="primary", use_container_width=True):
    if "No visible symptoms" in symptoms and len(symptoms)>1:
        st.warning("Choose 'No visible symptoms' alone, or remove it.")
    else:
        with st.spinner("Agents are checking weather, field observations, soil signals and planning actions..."):
            weather=fetch_weather(lat,lon)
            payload={"farm_name":farm_name,"crop":crop,"stage":crop_stage,"area_acres":area,
                     "lat":lat,"lon":lon,"soil_type":soil_type,"soil_ph":soil_ph,
                     "moisture":moisture,"rainfall_mm":rainfall,"symptoms":symptoms,
                     "notes":notes,"nitrogen":n,"phosphorus":p,"potassium":k,
                     "irrigation_method":irrigation_method,"water_available":water_available,
                     "advisory_level":advisory_level,"weather":weather}
            result=FarmSupervisor().run(payload)
            save_assessment(payload,result)
            st.session_state["last_result"]=(payload,result)

if "last_result" in st.session_state:
    payload,result=st.session_state["last_result"]
    st.divider()
    st.header("Farm intelligence report")
    st.caption(f"Generated for {payload['farm_name']} • {payload['crop']} • {date.today().isoformat()}")
    a,b,c=st.columns(3)
    a.metric("Weather status",result["weather_agent"]["status"])
    b.metric("Irrigation priority",result["irrigation_agent"]["priority"])
    c.metric("Crop-health concern",result["health_agent"]["severity"])
    st.subheader("Recommended action plan")
    for i,item in enumerate(result["plan"],1):
        with st.container(border=True):
            st.markdown(f"**{i}. {item['title']}**")
            st.write(item["action"])
            st.caption(f"Why: {item['reason']}  |  Priority: {item['priority']}  |  Review: {item['review']}")
    with st.expander("Agent reasoning and evidence"):
        for key,label in [("weather_agent","Weather agent"),("soil_agent","Soil agent"),("health_agent","Crop-health triage agent"),("irrigation_agent","Irrigation agent"),("knowledge_agent","Knowledge retrieval agent")]:
            st.markdown(f"**{label}**")
            st.write(result[key]["summary"])
            if result[key].get("evidence"): st.write("Evidence:", "; ".join(result[key]["evidence"]))
    st.warning("Decision-support prototype only. Confirm disease, pesticide, fertilizer and irrigation decisions with a local agricultural officer / KVK and product labels. Do not apply chemicals based only on this output.")
    st.download_button("⬇️ Download report (JSON)",data=json.dumps({"farm":payload,"assessment":result},indent=2),file_name="agripilot_report.json",mime="application/json")

st.divider()
st.subheader("Assessment history")
history=recent_assessments(8)
if not history.empty:
    st.dataframe(history, use_container_width=True, hide_index=True)
else:
    st.caption("No assessments saved yet.")
