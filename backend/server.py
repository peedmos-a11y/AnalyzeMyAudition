import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil, json
from voice_analysis import analyze_voice
from acting_analysis import analyze_acting

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Serve frontend files
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

# Load roles database
with open("roles.json") as f:
    roles_db = json.load(f)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), show: str = Form(...)):
    file_path = f"backend/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    vocal_type = analyze_voice(file_path)
    voice_score = 7.0 if vocal_type in ["Soprano","Mezzo"] else 6.0

    acting_feedback = analyze_acting(file_path)
    acting_score = {"Strong Emotional Delivery":9,
                    "Moderate Emotional Delivery":7,
                    "Limited Emotional Delivery":5,
                    "Neutral":4}.get(acting_feedback,5)

    overall_score = round(0.6*voice_score + 0.4*acting_score,1)

    show_roles = roles_db.get(show,{})
    matches = [role for role, r_type in show_roles.items() if r_type==vocal_type or r_type=="Any"]

    feedback = f"""
Vocal Type: {vocal_type} ({voice_score}/10)
Acting: {acting_feedback} ({acting_score}/10)
Overall Audition Score: {overall_score}/10
Best Role Matches: {', '.join(matches)}
"""

    return {
        "vocal_type":vocal_type,
        "acting_feedback":acting_feedback,
        "voice_score":voice_score,
        "acting_score":acting_score,
        "overall_score":overall_score,
        "matches":matches,
        "feedback":feedback
    }

# Deployment-friendly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.server:app", host="0.0.0.0", port=port, reload=True)
