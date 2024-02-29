import requests
import gradio as gr


def analysis(text: str):
    """
    回傳格式:
        {"text": text, "entities": output}
        text (str)
        output (list[dict]):
            [{'entity': 'I-LOC',
              'start': 5,
              'end': 12},
            {'entity': 'I-MISC'
              'start': 22,
              'end': 31}]
    """
    response_json = requests.post("http://192.168.1.76:7001/analysis", json={"text": text}).json()
    for key in response_json:
        if len(response_json[key]["entities"]) == 0:
            response_json[key] = None
    return "## Comparison", response_json["COMP"], "## Findings", response_json["FIND"], "## Impression", response_json["IMP"]


examples = [
    "> A 2 cm mass in the right upper lobe, highly suspicious for primary lung cancer. > Scattered ground-glass opacities in both lungs, possible early sign of interstitial lung disease. > No significant mediastinal lymph node enlargement. >Mild pleural effusion on the left side. > No evidence of bone metastasis in the visualized portions of the thorax. Conclusion: 1. Right upper lobe mass suggestive of lung cancer; biopsy recommended. 2. Ground-glass opacities; suggest follow-up CT in 3 months. 3. Mild pleural effusion; may require thoracentesis if symptomatic.",
]

comp_title = gr.Markdown("## Comparison")
find_title = gr.Markdown("## Findings")
imp_title = gr.Markdown("## Impression")

color_map = {
    "Observation": "red",
    "Finding": "blue",
    "Diagnosis": "green",
    "Location": "orange",
    "Certainty": "yellow",
    "Change": "lime",
    "Attribute": "purple",
    "Size": "teal",
    "Treatment": "cyan",
    "Normal": "pink",
    "Date": "lavender",
}

demo = gr.Interface(
    analysis,
    gr.Textbox(placeholder="Enter sentence here..."),
    [
        comp_title,
        gr.HighlightedText(label="Comparison", color_map=color_map, show_legend=True),
        find_title,
        gr.HighlightedText(label="Findings", color_map=color_map, show_legend=True),
        imp_title,
        gr.HighlightedText(label="Impression", color_map=color_map, show_legend=True),
    ],
    examples=examples,
)

demo.launch(server_name="0.0.0.0", server_port=7000)
