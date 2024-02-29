import os
import re

import uvicorn
import transformers
import onnxruntime as ort
from fastapi import FastAPI
from pydantic import BaseModel

import utils


app = FastAPI()


class TokenRequest(BaseModel):
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


@app.post("/token")
async def perform_token(request: TokenRequest):
    text = request.text
    clean_text = re.sub(r"([\[()\]:,])", r" \1 ", text).strip()
    clean_text = re.sub(r"\s+", " ", clean_text)
    ents = pipeline(clean_text)

    shift = 0
    results = list(clean_text)
    for ent in ents:
        if ent["entity"] == "O":
            continue
        results.insert(ent["start"] + shift, " ")
        shift += 1

    return "".join(results)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6667, log_level="info")
