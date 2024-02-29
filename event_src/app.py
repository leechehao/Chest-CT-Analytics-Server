import os

import uvicorn
import transformers
import onnxruntime as ort
from fastapi import FastAPI
from pydantic import BaseModel

import utils


app = FastAPI()


class EventRequest(BaseModel):
    text: str


cuda_available = os.environ.get("CUDA_AVAILABLE", "false") == "true"
providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if cuda_available else ["CPUExecutionProvider"]

session = ort.InferenceSession("./onnx_model/model.onnx", providers=providers)
tokenizer = transformers.AutoTokenizer.from_pretrained("./tokenizer")

with open("./label_list.txt") as file:
    label_list = eval(file.read())

id2label = {i: tag for i, tag in enumerate(label_list)}

pipeline = utils.Pipeline(
    session=session,
    tokenizer=tokenizer,
    id2label=id2label,
    aggregation_strategy=utils.AggregationStrategy.NONE,
)


@app.post("/event")
async def perform_event(request: EventRequest):
    text = request.text
    ents = pipeline(text)

    paragraphs = []
    tags = []
    point = None
    tag = None
    for ent in ents:
        if ent["entity"] == "O":
            continue
        if point is not None:
            paragraphs.append(text[point:ent["start"]].strip())
            tags.append(tag)
        point = ent["start"]
        tag = ent["entity"]

    paragraphs.append(text[point:].strip())
    tags.append(tag)

    results = {"COMP": [], "FIND": [], "IMP": []}
    section = None
    for tag, paragraph in zip(tags, paragraphs):
        if tag in ["FIND", "IMP"]:
            section = tag
        tag = section if tag == "EVENT" and section is not None else tag
        if tag in results:
            results[tag].append(paragraph)

    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6666, log_level="info")
