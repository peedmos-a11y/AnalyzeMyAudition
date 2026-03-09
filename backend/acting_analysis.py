import cv2
import mediapipe as mp
import numpy as np

mp_face = mp.solutions.face_mesh

def analyze_acting(video_path):
    cap = cv2.VideoCapture(video_path)
    face_mesh = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1)
    emotions = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mouth_top = face_landmarks.landmark[13]
                mouth_bottom = face_landmarks.landmark[14]
                mouth_distance = abs(mouth_bottom.y - mouth_top.y)
                brow_left = face_landmarks.landmark[105].y
                brow_right = face_landmarks.landmark[334].y
                brow_distance = abs(brow_left - brow_right)
                emotion_score = mouth_distance + brow_distance
                emotions.append(emotion_score)

    cap.release()
    face_mesh.close()

    if len(emotions) == 0:
        return "Neutral"
    avg_emotion = np.mean(emotions)
    if avg_emotion > 0.03:
        return "Strong Emotional Delivery"
    elif avg_emotion > 0.015:
        return "Moderate Emotional Delivery"
    else:
        return "Limited Emotional Delivery"
