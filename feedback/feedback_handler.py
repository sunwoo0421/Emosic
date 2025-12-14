# feedback/feedback_handler.py

MATCH_WEIGHTS = {
    "match": 1.0,        # 일치
    "partial": 0.6,      # 부분 일치
    "mismatch": 0.3      # 불일치
}

SCORE_WEIGHTS = {
    5: 1.0,
    4: 0.8,
    3: 0.6,
    2: 0.4,
    1: 0.2
}

def compute_feedback_factor(match_choice, satisfaction_score):
    """
    
    satisfaction_score: 1~5 정수
    """

    match_weight = MATCH_WEIGHTS.get(match_choice, 0.6)
    score_weight = SCORE_WEIGHTS.get(satisfaction_score, 0.6)

    feedback_factor = match_weight * score_weight
    return feedback_factor


def apply_feedback_to_features(features, feedback_factor):
    """
    features: dict {valence, energy, danceability}
    feedback_factor: 0.0 ~ 1.0
    """

    return {
        "valence": min(features["valence"] * feedback_factor, 1.0),
        "energy": min(features["energy"] * feedback_factor, 1.0),
        "danceability": min(features["danceability"] * feedback_factor, 1.0)
    }
