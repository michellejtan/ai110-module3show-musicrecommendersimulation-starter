from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    #added in phase 2
    instrumentalness: float
    duration_seconds: int
    popularity: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    def to_float(value: str, default: float = 0.0) -> float:
        """Convert value to float, returning default if missing or invalid."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def to_int(value: str, default: int = 0) -> int:
        """Convert value to int, returning default if missing or invalid."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               to_int(row.get("id")),
                "title":            row.get("title", ""),
                "artist":           row.get("artist", ""),
                "genre":            row.get("genre", ""),
                "mood":             row.get("mood", ""),
                "energy":           to_float(row.get("energy")),
                "tempo_bpm":        to_float(row.get("tempo_bpm")),
                "valence":          to_float(row.get("valence")),
                "danceability":     to_float(row.get("danceability")),
                "acousticness":     to_float(row.get("acousticness")),
                "instrumentalness": to_float(row.get("instrumentalness")),
                "duration_seconds": to_int(row.get("duration_seconds")),
                "popularity":       to_float(row.get("popularity")),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against a user preference dict.
    Returns (total_score, reasons) where reasons explains each component.

    EXPERIMENTAL WEIGHT SHIFT (max still 4.5 pts):
      +1.0  genre match          (was +2.0 — halved)
      +1.0  mood match
      +2.0  energy proximity     (was +1.0 — doubled)  2.0*(1.0 - |song.energy - target_energy|)
      +0.5  acousticness match (song.acousticness >= 0.5 ↔ likes_acoustic)
    """
    score = 0.0
    reasons: List[str] = []

    # --- genre match (+1.0, was +2.0) ---
    song_genre = song.get("genre", "")
    user_genre = user_prefs.get("favorite_genre", "")
    if song_genre and song_genre == user_genre:
        score += 1.0
        reasons.append("genre match (+1.0)")

    # --- mood match (+1.0) ---
    song_mood = song.get("mood", "")
    user_mood = user_prefs.get("favorite_mood", "")
    if song_mood and song_mood == user_mood:
        score += 1.0
        reasons.append("mood match (+1.0)")

    # --- energy proximity (+0.0 – +2.0, was +0.0 – +1.0) ---
    try:
        song_energy = float(song.get("energy", 0.0))
        target_energy = float(user_prefs.get("target_energy", 0.0))
        energy_pts = round(2.0 * (1.0 - abs(song_energy - target_energy)), 4)
        score += energy_pts
        reasons.append(f"energy proximity (+{energy_pts})")
    except (TypeError, ValueError):
        reasons.append("energy proximity (+0.0) [missing data]")

    # --- acousticness match (+0.5) ---
    # song.acousticness >= 0.5  → acoustic; < 0.5 → electronic
    try:
        is_acoustic = float(song.get("acousticness", 0.0)) >= 0.5
        likes_acoustic = bool(user_prefs.get("likes_acoustic", False))
        if is_acoustic == likes_acoustic:
            score += 0.5
            style = "acoustic" if likes_acoustic else "electronic"
            reasons.append(f"acousticness match — {style} preferred (+0.5)")
    except (TypeError, ValueError):
        reasons.append("acousticness match (+0.0) [missing data]")

    return round(score, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns the top-k songs as a list of (song_dict, score, explanation) tuples,
    sorted from highest to lowest score.
    """
    scored = [
        (song, score, ", ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    return ranked[:k]
