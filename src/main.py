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

# ============================================================================
# SYSTEM EVALUATION PROFILES
# ============================================================================
# Three distinct required profiles + adversarial edge-case profiles
# Run: python -m src.main  (the main() function loops through all of these)

SYSTEM_EVALUATION_PROFILES = {
    # ------------------------------------------------------------------
    # Required Profile 1: High-Energy Pop
    # Expected top picks: "Sunrise City" (pop/happy/0.82) and "Gym Hero" (pop/intense/0.93)
    # ------------------------------------------------------------------
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.9,
        "likes_acoustic": False,
        "description": "High-energy pop: upbeat mainstream music, near-maximum energy, electronic production",
    },

    # ------------------------------------------------------------------
    # Required Profile 2: Chill Lofi
    # Expected top pick: "Library Rain" (lofi/chill/0.35/acoustic=0.86)
    # ------------------------------------------------------------------
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
        "description": "Chill lofi listener: background beats, very low energy, acoustic texture, chill mood",
    },

    # ------------------------------------------------------------------
    # Required Profile 3: Deep Intense Rock
    # Expected top pick: "Storm Runner" (rock/intense/0.91/acoustic=0.10)
    # ------------------------------------------------------------------
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.91,
        "likes_acoustic": False,
        "description": "Deep intense rock: hard-driving guitars, near-max energy, raw intensity, electronic/distorted",
    },

    # ------------------------------------------------------------------
    # Adversarial Profile 1: Contradictory Energy + Mood
    # High energy (0.9) but sad/melancholic mood — these two rarely coexist.
    # Only "Rainy Blues" has melancholic mood (energy=0.48, acoustic=0.81).
    # The scorer should surface high-energy songs that miss on mood, OR
    # the lone melancholic song that is a big energy miss — a real tiebreaker test.
    # ------------------------------------------------------------------
    "Adversarial — High Energy Sad": {
        "favorite_genre": "blues",
        "favorite_mood": "melancholic",
        "target_energy": 0.9,
        "likes_acoustic": False,
        "description": "EDGE CASE: wants high-energy (0.9) but melancholic mood — genre+mood matches only low-energy 'Rainy Blues'",
    },

    # ------------------------------------------------------------------
    # Adversarial Profile 2: Genre Not in Catalog ("k-pop")
    # Zero genre matches across all 26 songs.
    # Recommendations must come entirely from mood/energy/acoustic scoring.
    # Tests how the system behaves with NO primary-feature hits.
    # ------------------------------------------------------------------
    "Adversarial — Ghost Genre (k-pop)": {
        "favorite_genre": "k-pop",
        "favorite_mood": "uplifting",
        "target_energy": 0.85,
        "likes_acoustic": False,
        "description": "EDGE CASE: 'k-pop' genre doesn't exist in catalog — zero +2.0 genre boosts; shows fallback scoring",
    },

    # ------------------------------------------------------------------
    # Adversarial Profile 3: Acoustic Raver (contradictory style + energy)
    # Wants electronic genre at near-maximum energy BUT also wants acoustic.
    # Electronic songs have acousticness < 0.5 (acoustic=False), so the
    # acoustic bonus (+0.5) can never be earned at the same time as the
    # genre bonus (+2.0). Tests if genre or acoustic preference "wins."
    # ------------------------------------------------------------------
    "Adversarial — Acoustic Raver": {
        "favorite_genre": "electronic",
        "favorite_mood": "uplifting",
        "target_energy": 0.88,
        "likes_acoustic": True,
        "description": "EDGE CASE: wants electronic genre (acoustic=0.08) but prefers acoustic sound — mutually exclusive; genre+acoustic can't both score",
    },

    # ------------------------------------------------------------------
    # Adversarial Profile 4: Mood-Genre Mismatch (Uplifting Metal)
    # Only metal song is "Blood Red" with "aggressive" mood, NOT "uplifting."
    # The two highest-scoring paths (genre match vs. mood match) conflict:
    # getting +2.0 genre means missing +1.0 mood, and vice versa.
    # ------------------------------------------------------------------
    "Adversarial — Uplifting Metal": {
        "favorite_genre": "metal",
        "favorite_mood": "uplifting",
        "target_energy": 0.9,
        "likes_acoustic": False,
        "description": "EDGE CASE: metal genre has only 'aggressive' mood songs; uplifting songs are electronic/house — genre vs mood score clash",
    },
}


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

    # ── System Evaluation: 3 required profiles + 4 adversarial profiles ──
    print("\n" + "=" * 60)
    print("  SYSTEM EVALUATION")
    print("  3 Distinct Profiles + 4 Adversarial Edge Cases")
    print("=" * 60 + "\n")
    for profile_name, prefs in SYSTEM_EVALUATION_PROFILES.items():
        _print_recommendations(profile_name, prefs, songs)

    # ── Original taste profiles (for reference) ──
    print("\n" + "=" * 60)
    print("  ORIGINAL TASTE PROFILES (reference)")
    print("=" * 60 + "\n")

    # Starter example profile
    starter_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
        "description": "Default test profile: pop, happy mood, high energy, electronic",
    }
    _print_recommendations("pop_happy (starter)", starter_prefs, songs)

    for profile_name, prefs in TASTE_PROFILES.items():
        _print_recommendations(profile_name, prefs, songs)


if __name__ == "__main__":
    main()
