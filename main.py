# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatInput, ChatOutput, MessageAnalysis
from utils import preprocess_chat, analyze_chat
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Influence Detector - Mock Backend",
    description="Backend API for detecting manipulation or influence in chat text.",
    version="1.0.0",
)

# CORS (important for Flutter and local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to your app domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (for Render, monitoring, debugging)
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Main chat analysis endpoint
@app.post("/analyze", response_model=ChatOutput)
async def analyze(chat_input: ChatInput):
    chat_text = chat_input.chat
    if not chat_text or not chat_text.strip():
        raise HTTPException(status_code=400, detail="Empty chat text provided.")

    # Preprocess into messages
    messages = preprocess_chat(chat_text)

    # Run analysis
    result = analyze_chat(messages)

    # Convert dicts to Pydantic models for response validation
    messages_out = []
    for m in result["messages"]:
        ma = MessageAnalysis(
            speaker=m["speaker"],
            text=m["text"],
            label=m["label"],
            confidence=m["confidence"],
            explanation=m.get("explanation"),
        )
        messages_out.append(ma)

    return ChatOutput(
        messages=messages_out,
        influence_score=result["influence_score"]
    )

# Run the app (only used in local dev, Render ignores this and uses your Start Command)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

