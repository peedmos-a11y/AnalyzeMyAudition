from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import json
import os

from voice_analysis import analyze_voice
from acting_analysis import analyze_acting
from database import conn, cursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

with open("roles.json") as f:
    roles_db = json.load(f)


# ------------------
# ACCOUNT SYSTEM
# ------------------

@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )
        conn.commit()
        return {"message": "Account created!"}
    except:
        return {"message": "Username already exists"}


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        return {"success": True}
    return {"success": False}


# ------------------
# AUDITION ANALYSIS
# ------------------

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), show: str = Form(...)):

    file_path = file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    vocal_type = analyze_voice(file_path)
    acting_feedback = analyze_acting(file_path)

    username = "guest"

    if "|" in show:
        show, username = show.split("|")

    show_roles = roles_db.get(show, {})

    role_probabilities = {}
    matches = []

    for role, r_type in show_roles.items():

        if r_type == vocal_type:
            prob = 0.8
        elif r_type == "Any":
            prob = 0.5
        else:
            prob = 0.3

        role_probabilities[role] = round(prob * 100)

        if prob >= 0.5:
            matches.append(role)

    feedback = f"""
Vocal Type: {vocal_type}

Acting Feedback: {acting_feedback}

Suggested Roles: {', '.join(matches)}
"""

    if role_probabilities:
        top_role = max(role_probabilities, key=role_probabilities.get)
        feedback += f"\nTop Recommended Role: {top_role} ({role_probabilities[top_role]}%)"

    cursor.execute(
        "INSERT INTO auditions(username,show,feedback) VALUES(?,?,?)",
        (username, show, feedback)
    )

    conn.commit()

    return {
        "feedback": feedback,
        "role_probabilities": role_probabilities
    }


# ------------------
# AUDITION HISTORY
# ------------------

@app.get("/history/{username}")
async def history(username: str):

    cursor.execute(
        "SELECT show,feedback FROM auditions WHERE username=?",
        (username,)
    )

    rows = cursor.fetchall()

    history = []

    for r in rows:
        history.append({
            "show": r[0],
            "feedback": r[1]
        })

    return {"history": history}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
