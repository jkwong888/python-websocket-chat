from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from google import genai
from google.genai import types

from langfuse.decorators import observe, langfuse_context

from pydantic import BaseModel

import os

PROJECT_ID = "jkwng-vertex-playground"
REGION = "us-central1"

MY_WS_URL = "ws://localhost:8000/ws"
model_id = "gemini-2.0-flash-001"

if os.getenv("MY_WS_URL") is not None:
    MY_WS_URL = os.getenv("MY_WS_URL")

if os.getenv("MODEL_ID") is not None:
    model_id = os.getenv("MODEL_ID")

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=REGION,
)

safety_settings_genai = [
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_NONE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_NONE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="BLOCK_NONE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_NONE",
    ),
]


system_prompt = """
You are a philosophical question answering bot asked to answer questions about the future.  Answer in numbered points with one sentence for each point.  Do not expand on each point.
""" # @param {type: "string"}
max_tokens = 256  # @param {type:"integer"}
temperature = 1.0  # @param {type:"number"}
top_p = 0.9  # @param {type:"number"}
top_k = 1  # @param {type:"integer"}


app = FastAPI()

html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
        <style>
            .wrapper {{
                padding: 5px;
                margin: 5px 0;
            }}
            textarea {{
                width: 100%;
                padding: 5px;
                border: 3px;
            }}

        </style>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <div>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <button onclick="clearText()">Clear</button>
        </div>
        <div class='wrapper' id='messages'>
        </div>
        <script>
            var ws;

            function clearText() {{
                var messages = document.getElementById('messages')
                messages.innerHTML = '';
            }}

            function addUsertext(text) {{
                var messages = document.getElementById('messages')
                var userDiv = document.createElement("div");
                var labelnode = document.createElement("label")
                labelnode.id = "ai"
                labelnode.textContent = text;

                userDiv.appendChild(labelnode);
                messages.appendChild(userDiv);
            }}

            function addAItext(text) {{
                var messages = document.getElementById('messages');
                var aiDiv = document.createElement("div");
                var labelnode = document.createElement("label");
                labelnode.id = "ai"
                labelnode.textContent += text;
                aiDiv.appendChild(labelnode);
                messages.appendChild(aiDiv);
            }}

            function startWebsocket() {{
                ws = new WebSocket("{MY_WS_URL}");

                ws.onmessage = function(event) {{
                    var content = 'AI:   ' + event.data + '\\n';
                    console.log(event.data);
                    addAItext(content)
                }};

                ws.onclose = function() {{
                    // restart websocket when it closes
                    ws = null
                    setTimeout(startWebsocket, 5000)
                }}
            }}

            function sendMessage(event) {{
                var input = document.getElementById("messageText")
                if (ws != null) {{
                    ws.send(input.value)

                    var content = 'User: ' + input.value + '\\n';
                    addUsertext(content)
                    input.value = ''
                }}

                event.preventDefault();

            }}

            startWebsocket();
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)

@observe(as_type="generation")
async def sendToLLMStreamingResponse(prompt: str):
    print(f"sending prompt {prompt} to LLM")
    responses = client.models.generate_content_stream(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            safety_settings=safety_settings_genai,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_tokens,
        ),
    )

    for response in responses:
        print(f"response: {response.candidates[0].content.parts[0].text}")
        yield response.candidates[0].content.parts[0].text
       
@observe(as_type="generation")
async def sendToLLM(prompt: str):
    print(f"sending prompt {prompt} to LLM")
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            safety_settings=safety_settings_genai,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_tokens,
        ),
    )

    return response.candidates[0].content.parts[0].text

    # return responses

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(f"received {data}")

        async for response in sendToLLMStreamingResponse(data):
            await websocket.send_text(response)


class LLMRequest(BaseModel):
    query: str

class LLMResponse(BaseModel):
    response: str

@app.post("/generate")
async def generate(llmReq: LLMRequest) -> LLMResponse:
    response = await sendToLLM(llmReq.query)
    return LLMResponse(
        response=response
    )