import librosa
import numpy as np

def analyze_voice(file_path):
    y, sr = librosa.load(file_path, sr=None)
    pitches = librosa.yin(y, fmin=50, fmax=500)
    avg_pitch = np.mean(pitches)
    
    if avg_pitch > 250:
        return "Soprano"
    elif avg_pitch > 180:
        return "Mezzo
    elif avg_pitch > 120:
        return "Tenor"
    else:
        return "Bass"
