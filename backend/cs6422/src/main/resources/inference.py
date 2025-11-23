import json
import pickle
import sys
import warnings

warnings.filterwarnings('ignore')


def load_model(model_path):
    """Load the trained restaurant recommender model"""
    with open(model_path, 'rb') as f:
        return pickle.load(f)


def match_any(field_value, filters):
    """Helper: TRUE if `field_value` matches ANY value in list."""
    if isinstance(filters, list):
        for f in filters:
            if f.lower() in str(field_value).lower():
                return True
        return False
    else:
        return filters.lower() in str(field_value).lower()


def filter_by_preferences(df, prefs):
    """Apply user filters before similarity/location ranking"""
    filtered = df.copy()

    # MULTI-SELECT cuisine filter
    if prefs.get("cuisine_type"):
        filtered = filtered[
            filtered["cuisine_type"].apply(lambda x: match_any(x, prefs["cuisine_type"]))
        ]

    # Rating
    if prefs.get("min_rating"):
        filtered = filtered[filtered["rating"] >= prefs["min_rating"]]

    # Budget
    if prefs.get("budget_filter"):
        filtered = filtered[filtered["price_level"] == prefs["budget_filter"]]

    # MULTI-SELECT atmosphere
    if prefs.get("atmosphere_filter"):
        filtered = filtered[
            filtered["atmosphere"].apply(lambda x: match_any(x, prefs["atmosphere_filter"]))
        ]

    # MULTI-SELECT amenities
    if prefs.get("amenities_filter"):
        filtered = filtered[
            filtered["amenities"].apply(lambda x: match_any(x, prefs["amenities_filter"]))
        ]

    # MULTI-SELECT restaurant type
    if prefs.get("restaurant_type_filter"):
        filtered = filtered[
            filtered["restaurant_type"].apply(lambda x: match_any(x, prefs["restaurant_type_filter"]))
        ]

    return filtered


def rank_restaurants(model, filtered_df, n):
    """Rank restaurants using similarity_matrix + location_matrix"""

    similarity_matrix = model["similarity_matrix"]
    location_matrix = model["location_matrix"]

    scores = []

    for idx, row in filtered_df.iterrows():
        content_score = similarity_matrix[idx].mean()
        location_score = location_matrix[idx].mean() if location_matrix is not None else 0.0

        final_score = 0.65 * content_score + 0.35 * location_score

        scores.append((row['place_id'], final_score))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    return [pid for pid, _ in scores[:n]]


def main():
    """Reads JSON input from backend and returns place_ids"""

    model_path = "src/main/resources/restaurant_recommender_fixed.pkl"

    # Read POSTed JSON from backend
    prefs_json = sys.stdin.read().strip()
    prefs = json.loads(prefs_json)

    # Load model
    model = load_model(model_path)
    df = model["df"]

    # Filter based on user preferences
    filtered_df = filter_by_preferences(df, prefs)

    if len(filtered_df) == 0:
        print(json.dumps({"place_ids": []}))
        return

    # Rank and get top results
    top_ids = rank_restaurants(
        model=model,
        filtered_df=filtered_df,
        n=prefs.get("n", 10)
    )

    print(json.dumps({"place_ids": top_ids}, indent=2))


if __name__ == "__main__":
    main()
