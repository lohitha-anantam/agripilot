from knowledge import retrieve_guidance

def weather_agent(data):
    w=data.get("weather") or {}
    if not w.get("ok"):
        return {"status":"Unavailable","summary":"Live forecast could not be retrieved. Use local forecast information before irrigation or spraying.","evidence":[],"rain_24h_mm":None,"rain_next_24h_mm":None}
    rain=w.get("rain_next_24h_mm",0)
    temp=w.get("max_temp_c")
    status="Rain likely" if rain is not None and rain>=5 else "No significant rain forecast"
    evidence=[f"Next 24-hour forecast rainfall: {rain:.1f} mm"]
    if temp is not None: evidence.append(f"Forecast maximum temperature: {temp:.1f} °C")
    return {"status":status,"summary":"Forecast is used as one input only; field moisture and crop stage still determine irrigation need.","evidence":evidence,"rain_24h_mm":w.get("rain_24h_mm"),"rain_next_24h_mm":rain,"max_temp_c":temp}

def soil_agent(data):
    ph=data["soil_ph"]; moisture=data["moisture"]
    flags=[]
    if ph<5.5: flags.append("Measured pH is acidic (<5.5); verify with a calibrated soil test and seek local soil-amendment advice.")
    elif ph>8.5: flags.append("Measured pH is alkaline (>8.5); verify with a calibrated soil test and seek local advice.")
    if moisture=="Waterlogged": flags.append("Waterlogging observed: check drainage and avoid adding irrigation.")
    elif moisture=="Very dry": flags.append("Very dry soil observed: check root-zone moisture before deciding irrigation.")
    nutrient=[]
    for name in ["nitrogen","phosphorus","potassium"]:
        val=data[name]
        if val!="Unknown": nutrient.append(f"{name.title()} test status: {val}")
    return {"summary":"Soil guidance is based on farmer-entered observations; pH and nutrient status are not inferred from soil type.","evidence":flags+nutrient,"flags":flags}

def health_agent(data):
    symptoms=data["symptoms"]
    if not symptoms or symptoms==["No visible symptoms"]:
        severity="Low / no symptoms reported"
        summary="No visible symptoms were reported. Continue routine scouting, especially on new growth and leaf undersides."
        evidence=[]
    else:
        severity="Needs field inspection" if len(symptoms)<3 else "Prompt inspection recommended"
        summary="Symptoms are non-specific and can result from pests, pathogens, nutrient imbalance, water stress or chemical injury. This system does not identify a disease from symptoms alone."
        evidence=["Symptoms reported: "+", ".join(symptoms),"Inspect several plants across the field; note distribution, affected plant parts and recent weather / spray history."]
    return {"severity":severity,"summary":summary,"evidence":evidence,"symptoms":symptoms}

def irrigation_agent(data, weather, soil):
    rain=weather.get("rain_next_24h_mm")
    moisture=data["moisture"]
    if moisture=="Waterlogged":
        priority="Do not irrigate now"
        action="Avoid additional irrigation. Inspect drainage and field outlets; reassess root-zone moisture after drainage."
        reason="Waterlogging was reported by the user."
    elif rain is not None and rain>=10 and moisture in ["Moderate","Moist"]:
        priority="Low — reassess after rain"
        action="Delay routine irrigation and recheck field moisture after the forecast rainfall. Do not rely on forecast alone."
        reason=f"Forecast rainfall is {rain:.1f} mm and soil was reported {moisture.lower()}."
    elif moisture in ["Very dry","Dry"]:
        priority="Check root zone today"
        action="Check moisture at the active root depth. If the root zone is dry and no effective rain is expected, irrigate according to crop stage, soil texture and local schedule."
        reason="Dryness was reported; exact water volume cannot be safely calculated without crop, soil and field measurements."
    else:
        priority="Monitor"
        action="Check root-zone moisture and crop condition before the next irrigation. Avoid calendar-only watering."
        reason="Reported moisture does not indicate an urgent irrigation trigger."
    if data["water_available"]=="Limited":
        action += " With limited water, prioritize critical crop stages and use the locally recommended deficit-irrigation strategy."
    return {"priority":priority,"summary":action,"action":action,"reason":reason,"evidence":[reason]}

def knowledge_agent(data):
    hits=retrieve_guidance(data["crop"],data["symptoms"],data["stage"])
    return {"summary":"Retrieved general crop-management reminders from the bundled local knowledge base. These are not location-specific prescriptions.","evidence":hits}

class FarmSupervisor:
    """Small, auditable agent workflow. Each agent returns structured findings; supervisor creates prioritized actions."""
    def run(self,data):
        weather=weather_agent(data)
        soil=soil_agent(data)
        health=health_agent(data)
        irrigation=irrigation_agent(data,weather,soil)
        knowledge=knowledge_agent(data)
        plan=[]
        if health["symptoms"] and health["symptoms"]!=["No visible symptoms"]:
            plan.append({"title":"Scout and document crop symptoms","action":"Inspect at least 10 representative plants in multiple parts of the field. Photograph both sides of leaves and affected stems/fruits. Record whether symptoms are spreading and whether they occur in patches.","reason":health["summary"],"priority":"High","review":"Before any pesticide or treatment"})
        if "Waterlogging observed" in soil["flags"]:
            plan.append({"title":"Check drainage","action":"Inspect field outlets and standing-water areas; avoid additional irrigation until the field condition is reassessed.","reason":"Waterlogging can damage roots and worsen crop stress.","priority":"High","review":"Today"})
        elif "Very dry soil observed" in soil["flags"] or "Dry" in data["moisture"]:
            plan.append({"title":"Verify root-zone moisture","action":irrigation["action"],"reason":irrigation["reason"],"priority":"High","review":"Before irrigation"})
        else:
            plan.append({"title":"Irrigation decision","action":irrigation["action"],"reason":irrigation["reason"],"priority":"Medium","review":"Recheck in 12–24 hours"})
        if soil["flags"] and not any("drainage" in x["title"].lower() for x in plan):
            plan.append({"title":"Verify soil test","action":"Use a laboratory soil test for pH and available N-P-K before applying amendments or fertilizer. Share the report with the local agriculture extension officer.","reason":"Entered soil indicators need laboratory confirmation.","priority":"Medium","review":"Before fertilizer application"})
        if data["nitrogen"]=="Low" or data["phosphorus"]=="Low" or data["potassium"]=="Low":
            plan.append({"title":"Review nutrient plan","action":"Discuss the soil-test result, crop stage and locally recommended nutrient schedule with a qualified extension officer. Do not apply a guessed dose.","reason":"One or more entered soil-test nutrients are marked low.","priority":"Medium","review":"Before fertilizer application"})
        if weather["status"]=="Rain likely":
            plan.append({"title":"Plan around rainfall","action":"Check the local forecast again before irrigation, fertilizer application or spraying. Avoid spraying in unsuitable wind or rain conditions and follow product-label restrictions.","reason":"Rain is forecast in the next 24 hours.","priority":"Medium","review":"Before field operation"})
        plan.append({"title":"Maintain field records","action":f"Record crop stage ({data['stage']}), irrigation, rainfall, symptoms and any input applied. Compare observations again in 2–3 days.","reason":"A dated record helps detect trends and improves future decisions.","priority":"Low","review":"In 2–3 days"})
        return {"weather_agent":weather,"soil_agent":soil,"health_agent":health,"irrigation_agent":irrigation,"knowledge_agent":knowledge,"plan":plan}
