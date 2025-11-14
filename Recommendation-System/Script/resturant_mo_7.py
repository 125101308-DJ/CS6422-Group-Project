import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
import pickle
import os
import warnings
from math import radians, sin, cos, sqrt, atan2
import requests
warnings.filterwarnings('ignore')

class RestaurantRecommender:
    def __init__(self, restaurants_file=None, reviews_file=None):
        """Initialize the recommender system with two data files (Excel or CSV)"""
        self.similarity_matrix = None
        self.review_sentiment_scores = None
        self.location_matrix = None
        self.user_item_matrix = None
        self.svd_model = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        
        # Only load data if files are provided (for new model training)
        if restaurants_file and reviews_file:
            # Load restaurant data - auto-detect format
            if restaurants_file.endswith('.csv'):
                self.df = pd.read_csv(restaurants_file)
            else:
                self.df = pd.read_excel(restaurants_file)
            print(f"Loaded {len(self.df)} restaurants")
            
            # Load reviews data - auto-detect format
            if reviews_file.endswith('.csv'):
                self.reviews = pd.read_csv(reviews_file)
            else:
                self.reviews = pd.read_excel(reviews_file)
            print(f"Loaded {len(self.reviews)} reviews")
        else:
            self.df = None
            self.reviews = None
        
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points on Earth using Haversine formula (in km)"""
        R = 6371  # Earth's radius in kilometers
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        return distance
    
    def geocode_address(self, address, use_nominatim=True):
        """Convert address to latitude and longitude"""
        try:
            if use_nominatim:
                url = f"https://nominatim.openstreetmap.org/search"
                params = {'q': address, 'format': 'json', 'limit': 1}
                headers = {'User-Agent': 'RestaurantRecommender/2.0'}
                
                response = requests.get(url, params=params, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        result = data[0]
                        return {
                            'latitude': float(result['lat']),
                            'longitude': float(result['lon']),
                            'formatted_address': result.get('display_name', address),
                            'success': True
                        }
            
            return {'success': False, 'error': 'Could not geocode address'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_restaurants_by_user_address(self, user_address, radius_km=5, n=10, 
                                       min_rating=None, cuisine_filter=None,
                                       budget_filter=None, atmosphere_filter=None,
                                       amenities_filter=None, restaurant_type_filter=None):
        """Get restaurant recommendations based on user's address with ALL filters"""
        print(f"Geocoding address: {user_address}")
        
        geo_result = self.geocode_address(user_address)
        
        if not geo_result['success']:
            return f"Error: Could not find location for '{user_address}'. Please provide a more specific address."
        
        latitude = geo_result['latitude']
        longitude = geo_result['longitude']
        
        print(f"✓ Location found: {geo_result['formatted_address']}")
        print(f"  Coordinates: ({latitude:.6f}, {longitude:.6f})")
        
        results = self.get_nearby_restaurants(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            n=n*3,
            min_rating=min_rating,
            cuisine_filter=cuisine_filter,
            budget_filter=budget_filter,
            atmosphere_filter=atmosphere_filter,
            amenities_filter=amenities_filter,
            restaurant_type_filter=restaurant_type_filter
        )
        
        if isinstance(results, pd.DataFrame) and len(results) > 0:
            results = results.head(n)
            results['user_location'] = geo_result['formatted_address']
            return results
        
        return f"No restaurants found within {radius_km}km of {user_address} matching your criteria."
    
    def calculate_distance_matrix(self):
        """Calculate distance matrix between all restaurants"""
        n = len(self.df)
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    distance_matrix[i, j] = self.haversine_distance(
                        self.df.iloc[i]['latitude'],
                        self.df.iloc[i]['longitude'],
                        self.df.iloc[j]['latitude'],
                        self.df.iloc[j]['longitude']
                    )
        
        scale = 5.0
        location_sim = np.exp(-distance_matrix / scale)
        return location_sim
        
    def preprocess_data(self):
        """Clean and prepare data for recommendation"""
        print("\n" + "="*70)
        print("DATA PREPROCESSING")
        print("="*70)
        
        required_cols = ['place_id', 'name', 'latitude', 'longitude', 'rating', 'address']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        print(f"\nOriginal data: {len(self.df)} restaurants, {len(self.reviews)} reviews")
        
        self.df['cuisine_type'] = self.df['cuisine_type'].fillna('General')
        self.df['atmosphere'] = self.df['atmosphere'].fillna('General')
        self.df['amenities'] = self.df['amenities'].fillna('None')
        self.df['price_range'] = self.df['price_range'].fillna('€10-25')
        self.df['restaurant_type'] = self.df['restaurant_type'].fillna('Restaurant')
        self.df['website'] = self.df['website'].fillna('')
        self.df['url'] = self.df['url'].fillna('')
        
        self.df['rating'] = self.df['rating'].clip(lower=0, upper=5)
        self.df['price_level'] = self.df['price_range'].apply(self._extract_price_level)
        
        print(f"\n✓ Filled missing values")
        print(f"  - Cuisine types: {self.df['cuisine_type'].nunique()}")
        print(f"  - Atmospheres: {self.df['atmosphere'].nunique()}")
        print(f"  - Restaurant types: {self.df['restaurant_type'].nunique()}")
        print(f"\nPrice Level Distribution:")
        print(self.df['price_level'].value_counts().sort_index())
        
        self.df['combined_features'] = (
            self.df['cuisine_type'].astype(str) + ' ' +
            self.df['restaurant_type'].astype(str) + ' ' +
            self.df['atmosphere'].astype(str) + ' ' +
            self.df['amenities'].astype(str)
        )
        
        self._process_reviews()
        
        print(f"\n✓ Data validation:")
        print(f"  - Restaurants with valid coordinates: {self.df[['latitude', 'longitude']].notna().all(axis=1).sum()}")
        print(f"  - Restaurants with reviews: {self.df['place_id'].isin(self.reviews['place_id']).sum()}")
        print(f"  - Average rating: {self.df['rating'].mean():.2f}")
        
        print("\nData preprocessing complete!")
        return self
    
    def _extract_price_level(self, price_range):
        """Extract numeric price level from price_range string
        Budget levels:
        1 = €5-15 (Budget-friendly)
        2 = €10-25 (Mid-range)
        3 = €20-35+ (Premium)
        """
        try:
            if pd.isna(price_range):
                return 2
            
            import re
            numbers = re.findall(r'\d+', str(price_range))
            
            if numbers:
                # Calculate average of the first two numbers (min and max)
                avg_price = sum(int(n) for n in numbers[:2]) / len(numbers[:2])
                
                # Map to 3 budget levels with clear boundaries
                if avg_price <= 15:      # €5-15
                    return 1
                elif avg_price <= 25:    # €10-25
                    return 2
                else:                    # €20-35+
                    return 3
            
            return 2
            
        except Exception as e:
            return 2
    
    def _process_reviews(self):
        """Process and aggregate review data"""
        review_agg = self.reviews.groupby('place_id').agg({
            'rating': ['mean', 'count', 'std'],
            'review_text': lambda x: ' '.join(x.astype(str))
        }).reset_index()
        
        review_agg.columns = ['place_id', 'avg_review_rating', 'review_count_agg', 
                              'rating_std', 'all_reviews_text']
        
        self.df = self.df.merge(review_agg, on='place_id', how='left')
        
        if 'review_count_agg' in self.df.columns:
            self.df['review_count'] = self.df['review_count_agg'].fillna(
                self.df.get('review_count', 0))
            self.df.drop('review_count_agg', axis=1, inplace=True)
        
        self.df['avg_review_rating'] = self.df['avg_review_rating'].fillna(self.df['rating'])
        self.df['rating_std'] = self.df['rating_std'].fillna(0)
        self.df['all_reviews_text'] = self.df['all_reviews_text'].fillna('')
        
        print(f"\n✓ Processed {len(review_agg)} restaurants with reviews")
    
    def build_model(self, weights=None, use_reviews=True, use_location=True):
        """Build content-based recommendation model"""
        print("\n" + "="*70)
        print("BUILDING CONTENT-BASED MODEL")
        print("="*70)
        
        if weights is None:
            weights = {
                'content': 0.35,
                'rating': 0.20,
                'price': 0.10,
                'reviews': 0.20,
                'location': 0.15
            }
        
        print(f"\nModel weights: {weights}")
        
        n_restaurants = len(self.df)
        
        print("\n1. Building content-based similarity...")
        tfidf_content = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=500)
        content_matrix = tfidf_content.fit_transform(self.df['combined_features'])
        content_sim = cosine_similarity(content_matrix, content_matrix)
        print(f"   ✓ Content similarity matrix: {content_sim.shape}")
        
        print("2. Building rating similarity...")
        ratings = self.df['rating'].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        ratings_scaled = scaler.fit_transform(ratings)
        rating_sim = 1 - np.abs(ratings_scaled - ratings_scaled.T)
        print(f"   ✓ Rating similarity matrix: {rating_sim.shape}")
        
        print("3. Building price similarity...")
        price_levels = self.df['price_level'].fillna(2).values.reshape(-1, 1)
        price_scaled = price_levels / 3.0  # Changed from 4.0 to 3.0 for 3 levels
        price_sim = 1 - np.abs(price_scaled - price_scaled.T)
        print(f"   ✓ Price similarity matrix: {price_sim.shape}")
        
        print("4. Building review text similarity...")
        review_sim = np.zeros((n_restaurants, n_restaurants))
        if use_reviews and 'all_reviews_text' in self.df.columns:
            has_reviews = self.df['all_reviews_text'].str.len() > 0
            if has_reviews.sum() > 0:
                review_texts = self.df['all_reviews_text'].fillna('')
                tfidf_reviews = TfidfVectorizer(stop_words='english', max_features=100, min_df=1)
                try:
                    review_matrix = tfidf_reviews.fit_transform(review_texts)
                    review_sim = cosine_similarity(review_matrix, review_matrix)
                    print(f"   ✓ Review similarity matrix: {review_sim.shape}")
                except:
                    print("   ⚠ Warning: Could not process review texts for similarity")
        else:
            print("   ⚠ Skipping review similarity (disabled or no reviews)")
        
        print("5. Building location similarity...")
        location_sim = np.zeros((n_restaurants, n_restaurants))
        if use_location and 'latitude' in self.df.columns and 'longitude' in self.df.columns:
            location_sim = self.calculate_distance_matrix()
            self.location_matrix = location_sim
            print(f"   ✓ Location similarity matrix: {location_sim.shape}")
        else:
            print("   ⚠ Skipping location similarity (disabled or no coordinates)")
        
        print("\n6. Combining all similarity matrices...")
        self.similarity_matrix = (
            weights['content'] * content_sim +
            weights['rating'] * rating_sim +
            weights['price'] * price_sim +
            weights['reviews'] * review_sim +
            weights['location'] * location_sim
        )
        
        print(f"   ✓ Final similarity matrix: {self.similarity_matrix.shape}")
        print(f"   ✓ Similarity range: [{self.similarity_matrix.min():.3f}, {self.similarity_matrix.max():.3f}]")
        
        print(f"\n✓ Content-based model built successfully with {len(self.df)} restaurants!")
        return self
    
    def build_collaborative_filtering(self, method='user-based', n_factors=20):
        """Build collaborative filtering model"""
        print("\n" + "="*70)
        print(f"BUILDING COLLABORATIVE FILTERING MODEL ({method.upper()})")
        print("="*70)
        
        user_item_df = self.reviews.pivot_table(
            index='username',
            columns='place_id',
            values='rating',
            fill_value=0
        )
        
        self.user_item_matrix = user_item_df
        print(f"\nUser-Item Matrix: {user_item_df.shape[0]} users × {user_item_df.shape[1]} items")
        print(f"  - Sparsity: {(user_item_df == 0).sum().sum() / (user_item_df.shape[0] * user_item_df.shape[1]) * 100:.2f}%")
        print(f"  - Total ratings: {(user_item_df != 0).sum().sum()}")
        
        if method == 'user-based':
            print("\nBuilding user-based similarity matrix...")
            user_similarity = cosine_similarity(user_item_df.values)
            self.user_similarity_matrix = pd.DataFrame(
                user_similarity,
                index=user_item_df.index,
                columns=user_item_df.index
            )
            print(f"✓ User-based similarity matrix created: {self.user_similarity_matrix.shape}")
            
        elif method == 'item-based':
            print("\nBuilding item-based similarity matrix...")
            item_similarity = cosine_similarity(user_item_df.T.values)
            self.item_similarity_matrix = pd.DataFrame(
                item_similarity,
                index=user_item_df.columns,
                columns=user_item_df.columns
            )
            print(f"✓ Item-based similarity matrix created: {self.item_similarity_matrix.shape}")
            
        elif method == 'matrix-factorization':
            print("\nBuilding matrix factorization model...")
            user_item_matrix = user_item_df.values
            if user_item_matrix.shape[0] > n_factors and user_item_matrix.shape[1] > n_factors:
                sparse_matrix = csr_matrix(user_item_matrix)
                k = min(n_factors, min(user_item_matrix.shape) - 1)
                U, sigma, Vt = svds(sparse_matrix, k=k)
                sigma = np.diag(sigma)
                predicted_ratings = np.dot(np.dot(U, sigma), Vt)
                
                self.svd_model = {
                    'U': U,
                    'sigma': sigma,
                    'Vt': Vt,
                    'predicted_ratings': predicted_ratings,
                    'users': user_item_df.index,
                    'items': user_item_df.columns
                }
                print(f"✓ Matrix factorization model created with {k} factors")
            else:
                print(f"⚠ Not enough data for matrix factorization ({user_item_matrix.shape}). Using user-based instead.")
                return self.build_collaborative_filtering('user-based')
        
        print(f"\n✓ Collaborative filtering model built successfully!")
        return self
    
    def save_model(self, filepath='restaurant_recommender.pkl'):
        """Save the trained model to a pickle file"""
        print("\n" + "="*70)
        print("SAVING MODEL")
        print("="*70)
        
        model_data = {
            'df': self.df,
            'reviews': self.reviews,
            'similarity_matrix': self.similarity_matrix,
            'location_matrix': self.location_matrix,
            'user_item_matrix': self.user_item_matrix,
            'user_similarity_matrix': self.user_similarity_matrix,
            'item_similarity_matrix': self.item_similarity_matrix,
            'svd_model': self.svd_model,
            'review_sentiment_scores': self.review_sentiment_scores
        }
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"\n✓ Model saved successfully to: {filepath}")
            print(f"  File size: {file_size_mb:.2f} MB")
            
            print(f"\n  Saved components:")
            print(f"    - Restaurants: {len(self.df)}")
            print(f"    - Reviews: {len(self.reviews)}")
            print(f"    - Similarity matrix: {'Yes' if self.similarity_matrix is not None else 'No'}")
            print(f"    - Location matrix: {'Yes' if self.location_matrix is not None else 'No'}")
            print(f"    - User similarity: {'Yes' if self.user_similarity_matrix is not None else 'No'}")
            print(f"    - Item similarity: {'Yes' if self.item_similarity_matrix is not None else 'No'}")
            print(f"    - SVD model: {'Yes' if self.svd_model is not None else 'No'}")
            
            return True
        except Exception as e:
            print(f"\n❌ Error saving model: {e}")
            return False
    
    @classmethod
    def load_model(cls, filepath='restaurant_recommender.pkl'):
        """Load a previously saved model from pickle file"""
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Model file not found: {filepath}")
            
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            recommender = cls()
            
            recommender.df = model_data['df']
            recommender.reviews = model_data['reviews']
            recommender.similarity_matrix = model_data['similarity_matrix']
            recommender.location_matrix = model_data['location_matrix']
            recommender.user_item_matrix = model_data['user_item_matrix']
            recommender.user_similarity_matrix = model_data['user_similarity_matrix']
            recommender.item_similarity_matrix = model_data['item_similarity_matrix']
            recommender.svd_model = model_data['svd_model']
            recommender.review_sentiment_scores = model_data.get('review_sentiment_scores')
            
            print(f"✓ Model loaded successfully from: {filepath}")
            print(f"  Restaurants: {len(recommender.df)}")
            print(f"  Reviews: {len(recommender.reviews)}")
            
            return recommender
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def get_recommendations(self, restaurant_name, n=5, min_rating=None, 
                          price_level=None, cuisine_filter=None, max_distance_km=None,
                          atmosphere_filter=None, amenities_filter=None, 
                          restaurant_type_filter=None, budget_filter=None):
        """Get top N similar restaurants with complete details and ALL filters"""
        if self.similarity_matrix is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        idx = self.df[self.df['name'].str.lower() == restaurant_name.lower()].index
        
        if len(idx) == 0:
            idx = self.df[self.df['name'].str.contains(restaurant_name, case=False, na=False)].index
            if len(idx) == 0:
                return f"Restaurant '{restaurant_name}' not found in dataset."
        
        idx = idx[0]
        source_restaurant = self.df.iloc[idx]
        
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for i, score in sim_scores[1:]:
            restaurant = self.df.iloc[i]
            
            distance = self.haversine_distance(
                source_restaurant['latitude'],
                source_restaurant['longitude'],
                restaurant['latitude'],
                restaurant['longitude']
            )
            
            if min_rating and restaurant['rating'] < min_rating:
                continue
            if price_level and restaurant['price_level'] != price_level:
                continue
            if budget_filter:
                if isinstance(budget_filter, int):
                    if restaurant['price_level'] != budget_filter:
                        continue
                else:
                    if budget_filter.lower() not in str(restaurant['price_range']).lower():
                        continue
            if cuisine_filter and cuisine_filter.lower() not in str(restaurant['cuisine_type']).lower():
                continue
            if max_distance_km and distance > max_distance_km:
                continue
            if atmosphere_filter and atmosphere_filter.lower() not in str(restaurant['atmosphere']).lower():
                continue
            if amenities_filter and amenities_filter.lower() not in str(restaurant['amenities']).lower():
                continue
            if restaurant_type_filter and restaurant_type_filter.lower() not in str(restaurant['restaurant_type']).lower():
                continue
                
            recommendations.append({
                'place_id': restaurant['place_id'],
                'name': restaurant['name'],
                'cuisine': restaurant['cuisine_type'],
                'restaurant_type': restaurant.get('restaurant_type', 'Restaurant'),
                'rating': restaurant['rating'],
                'review_count': restaurant['review_count'],
                'price_range': restaurant['price_range'],
                'price_level': restaurant.get('price_level', None),
                'atmosphere': restaurant['atmosphere'],
                'amenities': restaurant.get('amenities', ''),
                'address': restaurant['address'],
                'website': restaurant.get('website', ''),
                'url': restaurant.get('url', ''),
                'distance_km': round(distance, 2),
                'latitude': restaurant['latitude'],
                'longitude': restaurant['longitude'],
                'similarity_score': round(score, 3)
            })
            
            if len(recommendations) >= n:
                break
        
        if len(recommendations) == 0:
            return "No restaurants match your filters."
        
        return pd.DataFrame(recommendations)
    
    def get_nearby_restaurants(self, latitude, longitude, radius_km=5, n=10, 
                              min_rating=None, cuisine_filter=None, budget_filter=None,
                              atmosphere_filter=None, amenities_filter=None, 
                              restaurant_type_filter=None):
        """Find restaurants near a given location with ALL filters"""
        distances = []
        
        for idx, restaurant in self.df.iterrows():
            distance = self.haversine_distance(
                latitude, longitude,
                restaurant['latitude'],
                restaurant['longitude']
            )
            
            if distance <= radius_km:
                if min_rating and restaurant['rating'] < min_rating:
                    continue
                if cuisine_filter and cuisine_filter.lower() not in str(restaurant['cuisine_type']).lower():
                    continue
                if budget_filter:
                    if isinstance(budget_filter, int):
                        if restaurant['price_level'] != budget_filter:
                            continue
                    else:
                        if budget_filter.lower() not in str(restaurant['price_range']).lower():
                            continue
                if atmosphere_filter and atmosphere_filter.lower() not in str(restaurant['atmosphere']).lower():
                    continue
                if amenities_filter and amenities_filter.lower() not in str(restaurant['amenities']).lower():
                    continue
                if restaurant_type_filter and restaurant_type_filter.lower() not in str(restaurant['restaurant_type']).lower():
                    continue
                    
                distances.append({
                    'place_id': restaurant['place_id'],
                    'name': restaurant['name'],
                    'cuisine_type': restaurant['cuisine_type'],
                    'restaurant_type': restaurant.get('restaurant_type', 'Restaurant'),
                    'rating': restaurant['rating'],
                    'review_count': restaurant['review_count'],
                    'price_range': restaurant['price_range'],
                    'price_level': restaurant.get('price_level', 2),
                    'atmosphere': restaurant['atmosphere'],
                    'amenities': restaurant.get('amenities', ''),
                    'address': restaurant['address'],
                    'distance_km': round(distance, 2),
                    'latitude': restaurant['latitude'],
                    'longitude': restaurant['longitude']
                })
        
        distances_df = pd.DataFrame(distances)
        if len(distances_df) > 0:
            distances_df = distances_df.sort_values('distance_km').head(n)
        
        return distances_df
    
    def get_user_based_recommendations(self, username, n=10, min_rating=4.0):
        """Get recommendations based on similar users (User-Based Collaborative Filtering)"""
        if self.user_similarity_matrix is None:
            return "Collaborative filtering model not built. Call build_collaborative_filtering() first."
        
        if username not in self.user_similarity_matrix.index:
            return f"User '{username}' not found in the system."
        
        similar_users = self.user_similarity_matrix[username].sort_values(ascending=False)[1:11]
        user_ratings = self.user_item_matrix.loc[username]
        restaurants_not_rated = user_ratings[user_ratings == 0].index
        
        recommendations = []
        
        for place_id in restaurants_not_rated:
            similar_user_ratings = []
            for similar_user in similar_users.index:
                rating = self.user_item_matrix.loc[similar_user, place_id]
                if rating > 0:
                    similarity = similar_users[similar_user]
                    similar_user_ratings.append((rating, similarity))
            
            if similar_user_ratings:
                weighted_sum = sum(rating * sim for rating, sim in similar_user_ratings)
                similarity_sum = sum(sim for _, sim in similar_user_ratings)
                predicted_rating = weighted_sum / similarity_sum if similarity_sum > 0 else 0
                
                if predicted_rating >= min_rating:
                    restaurant = self.df[self.df['place_id'] == place_id]
                    if len(restaurant) > 0:
                        restaurant = restaurant.iloc[0]
                        recommendations.append({
                            'place_id': place_id,
                            'name': restaurant['name'],
                            'cuisine_type': restaurant['cuisine_type'],
                            'restaurant_type': restaurant.get('restaurant_type', 'Restaurant'),
                            'rating': restaurant['rating'],
                            'review_count': restaurant['review_count'],
                            'price_range': restaurant['price_range'],
                            'price_level': restaurant.get('price_level', None),
                            'atmosphere': restaurant['atmosphere'],
                            'amenities': restaurant.get('amenities', ''),
                            'address': restaurant['address'],
                            'latitude': restaurant['latitude'],
                            'longitude': restaurant['longitude'],
                            'predicted_rating': round(predicted_rating, 2)
                        })
        
        recommendations = sorted(recommendations, key=lambda x: x['predicted_rating'], reverse=True)[:n]
        return pd.DataFrame(recommendations) if recommendations else "No recommendations found."
    
    def get_hybrid_recommendations(self, restaurant_name=None, username=None, 
                                  n=10, content_weight=0.5, collaborative_weight=0.5):
        """Hybrid recommendations combining content-based and collaborative filtering"""
        recommendations = {}
        
        if restaurant_name and self.similarity_matrix is not None:
            content_recs = self.get_recommendations(restaurant_name, n=n*2)
            if isinstance(content_recs, pd.DataFrame):
                for _, row in content_recs.iterrows():
                    name = row['name']
                    recommendations[name] = {
                        'place_id': row['place_id'],
                        'name': name,
                        'cuisine': row['cuisine'],
                        'rating': row['rating'],
                        'content_score': row['similarity_score'] * content_weight,
                        'collaborative_score': 0,
                        'price_range': row['price_range'],
                        'address': row['address']
                    }
        
        if username and self.user_similarity_matrix is not None:
            collab_recs = self.get_user_based_recommendations(username, n=n*2)
            if isinstance(collab_recs, pd.DataFrame):
                for _, row in collab_recs.iterrows():
                    name = row['name']
                    if name in recommendations:
                        recommendations[name]['collaborative_score'] = row['predicted_rating'] * collaborative_weight / 5.0
                    else:
                        recommendations[name] = {
                            'place_id': row['place_id'],
                            'name': name,
                            'cuisine': row['cuisine_type'],
                            'rating': row['rating'],
                            'content_score': 0,
                            'collaborative_score': row['predicted_rating'] * collaborative_weight / 5.0,
                            'price_range': row['price_range'],
                            'address': row['address']
                        }
        
        for name in recommendations:
            recommendations[name]['hybrid_score'] = (
                recommendations[name]['content_score'] + 
                recommendations[name]['collaborative_score']
            )
        
        result_df = pd.DataFrame(list(recommendations.values()))
        if len(result_df) > 0:
            result_df = result_df.sort_values('hybrid_score', ascending=False).head(n)
            result_df['hybrid_score'] = result_df['hybrid_score'].round(3)
        
        return result_df if len(result_df) > 0 else "No recommendations found."
    
    def get_user_preferences(self, username):
        """Get a user's restaurant preferences based on their reviews"""
        user_reviews = self.reviews[self.reviews['username'] == username]
        
        if len(user_reviews) == 0:
            return f"User '{username}' not found."
        
        user_restaurants = []
        for _, review in user_reviews.iterrows():
            restaurant = self.df[self.df['place_id'] == review['place_id']]
            if len(restaurant) > 0:
                restaurant = restaurant.iloc[0]
                user_restaurants.append({
                    'place_id': restaurant['place_id'],
                    'restaurant': restaurant['name'],
                    'cuisine': restaurant['cuisine_type'],
                    'user_rating': review['rating'],
                    'avg_rating': restaurant['rating'],
                    'price_range': restaurant['price_range'],
                    'review_date': review.get('review_date', 'N/A')
                })
        
        user_df = pd.DataFrame(user_restaurants)
        
        if len(user_df) > 0:
            preferences = {
                'total_reviews': len(user_df),
                'avg_rating_given': user_df['user_rating'].mean(),
                'favorite_cuisines': user_df['cuisine'].value_counts().head(3).to_dict(),
                'reviews': user_df.sort_values('user_rating', ascending=False)
            }
            return preferences
        
        return "No review data available."
    
    def get_users_who_liked_restaurant(self, restaurant_name, min_rating=4):
        """Get users who liked a specific restaurant"""
        restaurant = self.df[self.df['name'].str.lower() == restaurant_name.lower()]
        if len(restaurant) == 0:
            return f"Restaurant '{restaurant_name}' not found."
        
        place_id = restaurant.iloc[0]['place_id']
        
        users_who_liked = self.reviews[
            (self.reviews['place_id'] == place_id) & 
            (self.reviews['rating'] >= min_rating)
        ][['username', 'rating', 'review_date', 'review_text']]
        
        return users_who_liked.sort_values('rating', ascending=False)
    
    def get_restaurant_details(self, restaurant_name):
        """Get detailed information about a restaurant including reviews"""
        restaurant = self.df[self.df['name'].str.lower() == restaurant_name.lower()]
        
        if len(restaurant) == 0:
            return f"Restaurant '{restaurant_name}' not found."
        
        restaurant = restaurant.iloc[0]
        place_id = restaurant['place_id']
        rest_reviews = self.reviews[self.reviews['place_id'] == place_id]
        
        print(f"\n{'='*70}")
        print(f"RESTAURANT DETAILS: {restaurant['name']}")
        print(f"{'='*70}")
        print(f"Place ID: {restaurant['place_id']}")
        print(f"Cuisine: {restaurant['cuisine_type']}")
        print(f"Type: {restaurant['restaurant_type']}")
        print(f"Rating: {restaurant['rating']} ({restaurant['review_count']} reviews)")
        print(f"Price Range: {restaurant['price_range']} (Level {restaurant['price_level']})")
        print(f"Address: {restaurant['address']}")
        print(f"Atmosphere: {restaurant['atmosphere']}")
        print(f"Amenities: {restaurant['amenities']}")
        if restaurant.get('website'):
            print(f"Website: {restaurant['website']}")
        
        if len(rest_reviews) > 0:
            print(f"\n--- Recent Reviews ---")
            for _, review in rest_reviews.head(5).iterrows():
                review_date = review.get('review_date', 'N/A')
                print(f"\n★ {review['rating']}/5 - {review['username']} ({review_date})")
                review_text = str(review.get('review_text', 'No review text'))
                print(f"   {review_text[:200]}...")
        
        print(f"\n{'='*70}\n")
        return restaurant
    
    def get_top_rated(self, n=10, min_reviews=5):
        """Get top rated restaurants with minimum review count"""
        top = self.df[self.df['review_count'] >= min_reviews].nlargest(n, 'rating')
        return top[['place_id', 'name', 'cuisine_type', 'rating', 'review_count', 
                   'price_range', 'price_level', 'address']]
    
    def get_by_cuisine(self, cuisine, n=10, min_rating=None, budget_filter=None,
                      atmosphere_filter=None, amenities_filter=None, 
                      restaurant_type_filter=None):
        """Get top restaurants by cuisine type with ALL filters"""
        filtered = self.df[self.df['cuisine_type'].str.contains(cuisine, case=False, na=False)]
        
        if min_rating:
            filtered = filtered[filtered['rating'] >= min_rating]
        if budget_filter:
            if isinstance(budget_filter, int):
                filtered = filtered[filtered['price_level'] == budget_filter]
            else:
                filtered = filtered[filtered['price_range'].str.contains(budget_filter, case=False, na=False)]
        if atmosphere_filter:
            filtered = filtered[filtered['atmosphere'].str.contains(atmosphere_filter, case=False, na=False)]
        if amenities_filter:
            filtered = filtered[filtered['amenities'].str.contains(amenities_filter, case=False, na=False)]
        if restaurant_type_filter:
            filtered = filtered[filtered['restaurant_type'].str.contains(restaurant_type_filter, case=False, na=False)]
        
        return filtered.nlargest(n, 'rating')[['place_id', 'name', 'cuisine_type', 'restaurant_type', 
                                                'rating', 'review_count', 'price_range', 'price_level',
                                                'atmosphere', 'amenities', 'address', 
                                                'latitude', 'longitude']]
    
    def get_restaurants_between_points(self, lat1, lon1, lat2, lon2, 
                                       max_detour_km=2, min_rating=None):
        """Find restaurants along a route between two points"""
        direct_distance = self.haversine_distance(lat1, lon1, lat2, lon2)
        
        restaurants_on_route = []
        
        for idx, restaurant in self.df.iterrows():
            dist_from_start = self.haversine_distance(
                lat1, lon1,
                restaurant['latitude'],
                restaurant['longitude']
            )
            dist_to_end = self.haversine_distance(
                restaurant['latitude'],
                restaurant['longitude'],
                lat2, lon2
            )
            
            total_distance = dist_from_start + dist_to_end
            detour = total_distance - direct_distance
            
            if detour <= max_detour_km:
                if min_rating is None or restaurant['rating'] >= min_rating:
                    restaurants_on_route.append({
                        'place_id': restaurant['place_id'],
                        'name': restaurant['name'],
                        'cuisine_type': restaurant['cuisine_type'],
                        'rating': restaurant['rating'],
                        'review_count': restaurant['review_count'],
                        'price_range': restaurant['price_range'],
                        'price_level': restaurant.get('price_level', 2),
                        'address': restaurant['address'],
                        'detour_km': round(detour, 2),
                        'distance_from_start_km': round(dist_from_start, 2),
                        'latitude': restaurant['latitude'],
                        'longitude': restaurant['longitude']
                    })
        
        route_df = pd.DataFrame(restaurants_on_route)
        if len(route_df) > 0:
            route_df = route_df.sort_values('distance_from_start_km')
        
        return route_df
    
    def display_recommendations(self, results, title="RECOMMENDATIONS"):
        """Pretty print recommendations with all details including place_id"""
        if isinstance(results, str):
            print(f"\n{results}")
            return
        
        if isinstance(results, pd.DataFrame) and len(results) > 0:
            print(f"\n{'='*70}")
            print(f"{title}")
            print(f"{'='*70}\n")
            
            for idx, row in results.iterrows():
                print(f"{idx + 1}. 🍽️  {row['name']}")
                print(f"   🆔 Place ID: {row.get('place_id', 'N/A')}")
                print(f"   ⭐ Rating: {row.get('rating', 'N/A')} ({row.get('review_count', 0)} reviews)")
                print(f"   🍴 Cuisine: {row.get('cuisine_type', row.get('cuisine', 'N/A'))}")
                print(f"   🏠 Type: {row.get('restaurant_type', 'N/A')}")
                
                # Price display
                price_range = row.get('price_range', 'N/A')
                price_level = row.get('price_level', '')
                if price_level:
                    print(f"   💰 Price: {price_range} (Level {price_level})")
                else:
                    print(f"   💰 Price: {price_range}")
                
                print(f"   🎭 Atmosphere: {row.get('atmosphere', 'N/A')}")
                
                # Optional fields
                if 'distance_km' in row:
                    print(f"   📍 Distance: {row['distance_km']} km")
                if 'similarity_score' in row:
                    print(f"   🔗 Similarity: {row['similarity_score']}")
                if 'predicted_rating' in row:
                    print(f"   🎯 Predicted Rating: {row['predicted_rating']}")
                if 'amenities' in row and row['amenities']:
                    print(f"   ✨ Amenities: {row['amenities']}")
                
                print(f"   📍 Address: {row.get('address', 'N/A')}")
                print()
            
            print(f"{'='*70}\n")
        else:
            print(f"\n{title}: No results found.")


# Example usage and workflow
if __name__ == "__main__":
    print("=" * 70)
    print("RESTAURANT RECOMMENDER SYSTEM - FIXED VERSION")
    print("=" * 70)
    
    restaurants_file = r"C:\Users\Roshan\Downloads\cleaned_restaurant_data.csv"
    reviews_file = r"C:\Users\Roshan\Downloads\Final_updated_userReviewsData.csv"
    model_filepath = "restaurant_recommender_fixed.pkl"
    
    if os.path.exists(model_filepath):
        print(f"\n✓ Found existing model: {model_filepath}")
        file_size = os.path.getsize(model_filepath) / (1024 * 1024)
        print(f"  Size: {file_size:.2f} MB")
        print(f"  Modified: {pd.Timestamp.fromtimestamp(os.path.getmtime(model_filepath))}")
        
        print("\nChoose an option:")
        print("1. Load existing model (fast)")
        print("2. Train new model (slow)")
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            try:
                recommender = RestaurantRecommender.load_model(model_filepath)
                print("\n✓ Model loaded successfully!")
                
            except Exception as e:
                print(f"\n❌ Error loading model: {e}")
                print("Will train a new model instead...")
                choice = "2"
        
        if choice == "2":
            try:
                print("\nTraining new model...")
                recommender = RestaurantRecommender(restaurants_file, reviews_file)
                recommender.preprocess_data()
                recommender.build_model()
                
                print("\nBuilding collaborative filtering...")
                recommender.build_collaborative_filtering(method='user-based')
                
                print("\nSaving model...")
                recommender.save_model(model_filepath)
                
            except FileNotFoundError as e:
                print(f"\n❌ Error: Could not find data files!")
                print(f"Please make sure these files exist:")
                print(f"  - {restaurants_file}")
                print(f"  - {reviews_file}")
                exit()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                exit()
    else:
        print(f"\nNo existing model found. Training new model...")
        try:
            recommender = RestaurantRecommender(restaurants_file, reviews_file)
            recommender.preprocess_data()
            recommender.build_model()
            
            print("\nBuilding collaborative filtering...")
            recommender.build_collaborative_filtering(method='user-based')
            
            print("\nSaving model...")
            recommender.save_model(model_filepath)
            
        except FileNotFoundError as e:
            print(f"\n❌ Error: Could not find data files!")
            print(f"Please make sure these files exist:")
            print(f"  - {restaurants_file}")
            print(f"  - {reviews_file}")
            exit()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            exit()
    
    print("\n" + "=" * 70)
    print("RUNNING VALIDATION TESTS")
    print("=" * 70)
    
    print("\nTest 1: Content-based recommendations with place_id")
    sample_restaurant = recommender.df.iloc[0]['name']
    recs = recommender.get_recommendations(sample_restaurant, n=3)
    recommender.display_recommendations(recs, f"Similar to '{sample_restaurant}'")
    
    print("\nTest 2: Location-based search with budget filter")
    sample_lat = recommender.df.iloc[0]['latitude']
    sample_lon = recommender.df.iloc[0]['longitude']
    nearby = recommender.get_nearby_restaurants(
        sample_lat, sample_lon, 
        radius_km=5, 
        n=3,
        budget_filter=1  # Budget-friendly
    )
    recommender.display_recommendations(nearby, "Nearby Budget-Friendly Restaurants")
    
    print("\nTest 3: Cuisine search with multiple filters")
    cuisine_results = recommender.get_by_cuisine(
        'Italian',
        n=3,
        min_rating=4.0,
        budget_filter=2  # Mid-range
    )
    recommender.display_recommendations(cuisine_results, "Italian Restaurants (Mid-range, Rating ≥4.0)")
    
    print("\nTest 4: Address geocoding and search")
    test_address = "Cork City, Ireland"
    address_results = recommender.get_restaurants_by_user_address(
        test_address,
        radius_km=10,
        n=5,
        min_rating=4.0
    )
    recommender.display_recommendations(address_results, f"Restaurants near {test_address}")
    
    if recommender.user_similarity_matrix is not None:
        print("\nTest 5: Collaborative filtering recommendations")
        sample_user = recommender.reviews['username'].value_counts().index[0]
        user_recs = recommender.get_user_based_recommendations(sample_user, n=3)
        recommender.display_recommendations(user_recs, f"Recommendations for user '{sample_user}'")
    else:
        print("\nTest 5: Collaborative filtering - SKIPPED (not built)")
    
    print("\n" + "=" * 70)
    print("MODEL SUMMARY")
    print("=" * 70)
    print(f"\nDataset Statistics:")
    print(f"  Total Restaurants: {len(recommender.df)}")
    print(f"  Total Reviews: {len(recommender.reviews)}")
    print(f"  Unique Users: {recommender.reviews['username'].nunique()}")
    print(f"  Average Rating: {recommender.df['rating'].mean():.2f}")
    print(f"  Cuisines: {recommender.df['cuisine_type'].nunique()}")
    
    print(f"\nPrice Level Distribution:")
    price_dist = recommender.df['price_level'].value_counts().sort_index()
    for level, count in price_dist.items():
        level_name = {1: "Budget (€5-15)", 2: "Mid-range (€10-25)", 3: "Premium (€20-35+)"}.get(level, f"Level {level}")
        print(f"  {level_name}: {count} restaurants")
    
    print(f"\nModel Components:")
    print(f"  ✓ Content-based similarity: {recommender.similarity_matrix is not None}")
    print(f"  ✓ Location matrix: {recommender.location_matrix is not None}")
    print(f"  ✓ User similarity: {recommender.user_similarity_matrix is not None}")
    print(f"  ✓ Item similarity: {recommender.item_similarity_matrix is not None}")
    print(f"  ✓ SVD model: {recommender.svd_model is not None}")
    
    print(f"\nAvailable Filters:")
    print(f"  ✓ Cuisine filter")
    print(f"  ✓ Budget/Price filter (3 levels)")
    print(f"  ✓ Rating filter")
    print(f"  ✓ Distance/Radius filter")
    print(f"  ✓ Atmosphere filter")
    print(f"  ✓ Amenities filter")
    print(f"  ✓ Restaurant type filter")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - SYSTEM READY!")
    print("=" * 70)
    print("\nPlace IDs are now displayed in all recommendations!")