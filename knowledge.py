"""Tiny local retrieval layer. Keep advice generic and validate region-specific practices with KVK."""
import json
from pathlib import Path

KB_PATH=Path(__file__).parent/"data"/"agri_knowledge.json"
def retrieve_guidance(crop, symptoms, stage):
    try:
        records=json.loads(KB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return ["Local knowledge file unavailable; consult the nearest KVK / agriculture extension office."]
    terms=set((crop+" "+stage+" "+" ".join(symptoms)).lower().replace("("," ").replace(")"," ").split())
    scored=[]
    for item in records:
        tags=set(t.lower() for t in item.get("tags",[]))
        score=len(terms & tags)
        if score: scored.append((score,item["guidance"]))
    scored.sort(key=lambda x:x[0],reverse=True)
    return [x[1] for x in scored[:4]] or ["Scout the crop regularly and follow region- and crop-stage-specific recommendations from the local KVK."]
