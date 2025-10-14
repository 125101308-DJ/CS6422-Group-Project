import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack, csr_matrix
import math

# ================= Utility Functions =================
@st.cache_data
def load_data(uploaded_file):
    """Load dataset from CSV or Excel file."""
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload CSV or Excel.")
        return None
    st.write(f"✅ Dataset loaded! Shape: {df.shape}")
    return df

def haversine(lon1, lat1, lon2, lat2):
    """Distance between two lat/lon points in km."""
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)*2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)*2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@st.cache_data
def build_feature_matrix(df):
    """Combine text and numeric features into a matrix."""
    # Text features
    text_cols = ['cuisine_type', 'atmosphere', 'dietary_options', 'service_options', 'amenities']
    for c in text_cols:
        if c not in df.columns:
            df[c] = ""
    df['combined_text'] = df[text_cols].fillna('').agg(' '.join, axis=1)

    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    text_mat = tfidf.fit_transform(df['combined_text'])

    # Numeric features
    num_cols = []
    if 'rating' in df.columns:
        num_cols.append('rating')
    if 'price_level' in df.columns:
        num_cols.append('price_level')

    if num_cols:
        num_df = df[num_cols].fillna(df[num_cols].median())
        scaler = StandardScaler()
        num_mat = scaler.fit_transform(num_df)
        combined = hstack([text_mat, csr_matrix(num_mat)])
    else:
        combined = text_mat

    return combined, tfidf

def compute_similarity(feature_matrix):
    """Compute cosine similarity matrix."""
    similarity = cosine_similarity(feature_matrix, feature_matrix)
    return similarity

def recommend(df, similarity, idx, topn=10, user_loc=None, radius_km=None):
    """Get top-n similar restaurants with optional location filter."""
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    recs = []

    for i, score in sim_scores[1:]:  # skip itself
        if user_loc and radius_km:
            dist = haversine(user_loc[1], user_loc[0], df.loc[i, 'longitude'], df.loc[i, 'latitude'])
            if dist > radius_km:
                continue
        recs.append((i, score))
        if len(recs) >= topn:
            break

    rec_indices = [i for i, _ in recs]
    return df.iloc[rec_indices].assign(similarity=[s for _, s in recs])

# ================= Streamlit App =================
def main():
    st.set_page_config(page_title="🍽 Restaurant Recommender", layout="wide")
    st.title("🍴 Smart Restaurant Recommendation System")
    st.markdown("Upload your dataset to get restaurant recommendations based on cuisine, amenities, and more.")

    uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xls", "xlsx"])
    if uploaded_file is None:
        st.info("👆 Upload a CSV or Excel file to begin.")
        return

    df = load_data(uploaded_file)
    if df is None:
        return

    if 'name' not in df.columns:
        st.error("CSV/Excel must have a 'name' column for restaurants.")
        return
    df = df.dropna(subset=['name']).reset_index(drop=True)

    # Build features and similarity
    feature_matrix, tfidf = build_feature_matrix(df)
    similarity = compute_similarity(feature_matrix)

    # Sidebar inputs
    st.sidebar.header("⚙ Controls")
    restaurant = st.sidebar.selectbox("Select a restaurant", df['name'].tolist())
    num_recs = st.sidebar.slider("Number of recommendations", 1, 20, 5)

    use_location = st.sidebar.checkbox("Filter by distance (km)")
    user_lat = user_lon = radius_km = None
    if use_location:
        user_lat = st.sidebar.number_input("Your latitude", value=float(df['latitude'].median()) if 'latitude' in df.columns else 0.0)
        user_lon = st.sidebar.number_input("Your longitude", value=float(df['longitude'].median()) if 'longitude' in df.columns else 0.0)
        radius_km = st.sidebar.slider("Radius (km)", 1, 50, 10)

    idx = df.index[df['name'] == restaurant][0]
    user_loc = (user_lat, user_lon) if use_location else None
    recs = recommend(df, similarity, idx, topn=num_recs, user_loc=user_loc, radius_km=radius_km)

    # Display selected restaurant
    st.subheader("📍 Selected Restaurant")
    sel = df.loc[idx]
    st.markdown(f"{sel['name']}** — ⭐ {sel.get('rating', 'N/A')} — {sel.get('cuisine_type', '')}")
    st.write(sel.get('address', ''))

    # Display recommendations
    st.subheader("🔎 Recommended Restaurants")
    if recs.empty:
        st.info("No matching restaurants found.")
    else:
        show_cols = ['name', 'address', 'cuisine_type', 'rating', 'price_range', 'price_level', 'latitude', 'longitude', 'similarity']
        available = [c for c in show_cols if c in recs.columns]
        st.dataframe(recs[available].reset_index(drop=True))
        if 'latitude' in recs.columns and 'longitude' in recs.columns:
            st.map(recs[['latitude', 'longitude']].dropna())

if __name__ == "__main__":
    main()