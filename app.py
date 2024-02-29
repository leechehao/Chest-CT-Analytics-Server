import requests
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import utils


app = FastAPI()


class AnalysisRequest(BaseModel):
    text: str


@app.post("/analysis")
async def perform_analysis(request: AnalysisRequest):
    text = request.text
    event_json = requests.post("http://192.168.1.76:6666/event", json={"text": text}).json()

    results = {"COMP": utils.AnalysisExample(), "FIND": utils.AnalysisExample(), "IMP": utils.AnalysisExample()}
    for section, events in event_json.items():
        if section not in results:
            continue
        for event in events:
            token_text = requests.post("http://192.168.1.76:6667/token", json={"text": event}).json()
            ner_outputs = requests.post("http://192.168.1.76:6668/ner", json={"text": token_text}).json()
            if section == "COMP":
                results[section].add_re_event(ner_outputs)
                continue
            root_ents = [ent for ent in ner_outputs["entities"] if ent["entity"] in ["Observation", "Finding", "Treatment", "Normal"]]
            for root_ent in root_ents:
                special_token_text = utils.add_special_token(ner_outputs["text"], root_ent)
                re_output = requests.post("http://192.168.1.76:6669/re", json={"text": special_token_text}).json()
                results[section].add_re_event(re_output, root_ent["start"] + 1, root_ent["end"] + 3)
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7001, log_level="info")
