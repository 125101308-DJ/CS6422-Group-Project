import sys
import json
import pickle
import warnings
warnings.filterwarnings('ignore')


def load_model(model_path):
    """Load the trained restaurant recommender model"""
    with open(model_path, 'rb') as f:
        return pickle.load(f)


def filter_by_preferences(df, prefs):
    """Apply user filters before similarity/location ranking"""

    filtered = df.copy()

    if prefs.get("cuisine_type"):
        filtered = filtered[
            filtered["cuisine_type"].str.contains(prefs["cuisine_type"], case=False, na=False)
        ]

    if prefs.get("min_rating"):
        filtered = filtered[filtered["rating"] >= prefs["min_rating"]]

    if prefs.get("budget_filter"):
        filtered = filtered[filtered["price_level"] == prefs["budget_filter"]]

    if prefs.get("atmosphere_filter"):
        filtered = filtered[
            filtered["atmosphere"].str.contains(prefs["atmosphere_filter"], case=False, na=False)
        ]

    if prefs.get("amenities_filter"):
        filtered = filtered[
            filtered["amenities"].str.contains(prefs["amenities_filter"], case=False, na=False)
        ]

    if prefs.get("restaurant_type_filter"):
        filtered = filtered[
            filtered["restaurant_type"].str.contains(prefs["restaurant_type_filter"], case=False, na=False)
        ]

    return filtered


def rank_restaurants(model, filtered_df, n):
    """Rank restaurants using similarity_matrix + location_matrix"""

    similarity_matrix = model["similarity_matrix"]
    location_matrix = model["location_matrix"]

    scores = []

    for idx, row in filtered_df.iterrows():

        # Take the MEAN similarity to all restaurants as the content score
        content_score = similarity_matrix[idx].mean()

        # Take the MEAN location similarity to all restaurants
        location_score = location_matrix[idx].mean() if location_matrix is not None else 0.0

        final_score = 0.65 * content_score + 0.35 * location_score

        scores.append((row['place_id'], final_score))

    # Sort by score
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    return [pid for pid, _ in scores[:n]]


def main():

    model_path = 'restaurant_recommender_fixed.pkl'

    prefs_json = '''{
        "address": "Cork City Centre, Cork, Ireland",
        "radius_km": 5,
        "cuisine_type": "Italian",
        "budget_filter": 2,
        "atmosphere_filter": "Casual",
        "amenities_filter": "Bar",
        "restaurant_type_filter": "Restaurant",
        "n": 10
    }'''
    # prefs_json = sys.argv[2]

    prefs = json.loads(prefs_json)

    # Load model
    model = load_model(model_path)

    df = model["df"]

    # Filter restaurants
    filtered_df = filter_by_preferences(df, prefs)

    if len(filtered_df) == 0:
        print(json.dumps({"error": "No restaurants match filters"}))
        return

    # Rank restaurants
    top_ids = rank_restaurants(
        model=model,
        filtered_df=filtered_df,
        n=prefs.get("n", 10)
    )

    # Output
    print(json.dumps({"place_ids": top_ids}, indent=2))


if __name__ == "__main__":
    main()
