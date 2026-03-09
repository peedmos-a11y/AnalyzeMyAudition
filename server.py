from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import json
import os

from voice_analysis import analyze_voice
from acting_analysis import analyze_acting

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Load roles
with open("roles.json") as f:
    roles_db = json.load(f)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), show: str = Form(...)):

    file_path = file.filename

    # save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # run analysis
    vocal_type = analyze_voice(file_path)
    acting_feedback = analyze_acting(file_path)

    # role matching
    show_roles = roles_db.get(show, {})
    matches = [
        role for role, r_type in show_roles.items()
        if r_type == vocal_type or r_type == "Any"
    ]

    feedback = f"""
Vocal Type: {vocal_type}

Acting Feedback: {acting_feedback}

Suggested Roles: {', '.join(matches)}
"""

    return {"feedback": feedback}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
