"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs, Song, UserProfile, Recommender
import csv


# ============================================================================
# TASTE PROFILES: Example user preferences for testing
# ============================================================================

TASTE_PROFILES = {
    # ========================================================================
    # CORE 3 REQUIRED PROFILES - Maximally Distinct
    # ========================================================================
    
    "hip_hop_fan": {
        "favorite_genre": "hip-hop",
        "favorite_mood": "energetic",
        "target_energy": 0.78,
        "likes_acoustic": False,
        "description": "Urban beats lover: hip-hop, energetic mood, high energy, electronic production"
    },
    
    "chill_listener": {
        "favorite_genre": "ambient",
        "favorite_mood": "chill",
        "target_energy": 0.3,
        "likes_acoustic": True,
        "description": "Acoustic low-energy listener: very low energy, chill, ambient atmosphere, acoustic preferred"
    },
    
    "edm_raver": {
        "favorite_genre": "electronic",
        "favorite_mood": "uplifting",
        "target_energy": 0.85,
        "likes_acoustic": False,
        "description": "High-tempo EDM listener: electronic/house, uplifting, maximum energy, dance beats"
    },
    
    # ========================================================================
    # COMPLEMENTARY PROFILES - Non-Overlapping Scenarios
    # ========================================================================
    
    "classical_connoisseur": {
        "favorite_genre": "classical",
        "favorite_mood": "contemplative",
        "target_energy": 0.35,
        "likes_acoustic": True,
        "description": "Orchestral lover: classical, contemplative mood, low-medium energy, acoustic instruments"
    },
    
    "reggae_chill": {
        "favorite_genre": "reggae",
        "favorite_mood": "chill",
        "target_energy": 0.52,
        "likes_acoustic": True,
        "description": "Island vibes: reggae, chill mood, medium energy, laid-back acoustic feel"
    },
    
    "metal_headbanger": {
        "favorite_genre": "metal",
        "favorite_mood": "aggressive",
        "target_energy": 0.94,
        "likes_acoustic": False,
        "description": "Intense rocker: metal, aggressive mood, maximum intensity, electronic backing"
    },
    
    "jazz_evening": {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.5,
        "likes_acoustic": True,
        "description": "Smooth jazz connoisseur: jazz, relaxed mood, medium energy, live acoustic instruments"
    },
}


def load_songs_from_csv(csv_path: str):
    """Load songs from CSV and convert to Song objects."""
    songs = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = Song(
                id=int(row['id']),
                title=row['title'],
                artist=row['artist'],
                genre=row['genre'],
                mood=row['mood'],
                energy=float(row['energy']),
                tempo_bpm=float(row['tempo_bpm']),
                valence=float(row['valence']),
                danceability=float(row['danceability']),
                acousticness=float(row['acousticness']),
                instrumentalness=float(row['instrumentalness']),
                duration_seconds=int(row['duration_seconds']),
                popularity=float(row['popularity'])
            )
            songs.append(song)
    return songs


def _print_recommendations(profile_name: str, prefs: dict, songs: list) -> None:
    """Print a clean recommendation block for one user profile."""
    recommendations = recommend_songs(prefs, songs, k=5)

    print("=" * 60)
    print(f"  PROFILE : {profile_name.upper()}")
    print(f"  {prefs.get('description', '')}")
    print(f"  Genre: {prefs.get('favorite_genre')}  |  "
          f"Mood: {prefs.get('favorite_mood')}  |  "
          f"Energy: {prefs.get('target_energy')}  |  "
          f"{'Acoustic' if prefs.get('likes_acoustic') else 'Electronic'}")
    print("=" * 60)

    if not recommendations:
        print("  No recommendations found.\n")
        return

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']} - {song['artist']}")
        print(f"       Score : {score:.2f} / 4.5")
        for reason in explanation.split(", "):
            print(f"         - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    # Starter example profile
    starter_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
        "description": "Default test profile: pop, happy mood, high energy, electronic",
    }
    _print_recommendations("pop_happy (starter)", starter_prefs, songs)

    # All taste profiles
    for profile_name, prefs in TASTE_PROFILES.items():
        _print_recommendations(profile_name, prefs, songs)


if __name__ == "__main__":
    main()
