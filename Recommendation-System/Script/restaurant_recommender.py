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
warnings.filterwarnings('ignore')

class RestaurantRecommender:
    def __init__(self, restaurants_file, reviews_file):
        """Initialize the recommender system with two data files (Excel or CSV)"""
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
        
        self.similarity_matrix = None
        self.review_sentiment_scores = None
        self.location_matrix = None
        self.user_item_matrix = None
        self.svd_model = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        
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
        
        # Convert distance to similarity (closer = more similar)
        scale = 5.0  # 5km scale factor
        location_sim = np.exp(-distance_matrix / scale)
        return location_sim
        
    def preprocess_data(self):
        """Clean and prepare data for recommendation"""
        # Fill missing values in restaurant data
        self.df['cuisine_type'] = self.df['cuisine_type'].fillna('General')
        self.df['atmosphere'] = self.df['atmosphere'].fillna('General')
        self.df['dietary_options'] = self.df['dietary_options'].fillna('None')
        self.df['service_options'] = self.df['service_options'].fillna('None')
        self.df['amenities'] = self.df['amenities'].fillna('None')
        self.df['price_range'] = self.df['price_range'].fillna('€10-20')
        self.df['restaurant_type'] = self.df['restaurant_type'].fillna('Restaurant')
        
        # Create combined text features for content-based filtering
        self.df['combined_features'] = (
            self.df['cuisine_type'].astype(str) + ' ' +
            self.df['restaurant_type'].astype(str) + ' ' +
            self.df['atmosphere'].astype(str) + ' ' +
            self.df['dietary_options'].astype(str) + ' ' +
            self.df['service_options'].astype(str) + ' ' +
            self.df['amenities'].astype(str)
        )
        
        # Process reviews - aggregate by restaurant
        self._process_reviews()
        
        print("Data preprocessing complete!")
        return self
    
    def _process_reviews(self):
        """Process and aggregate review data"""
        # Calculate review-based features
        review_agg = self.reviews.groupby('place_id').agg({
            'rating': ['mean', 'count', 'std'],
            'review_text': lambda x: ' '.join(x.astype(str))
        }).reset_index()
        
        review_agg.columns = ['place_id', 'avg_review_rating', 'review_count_agg', 
                              'rating_std', 'all_reviews_text']
        
        # Merge with restaurant data
        self.df = self.df.merge(review_agg, on='place_id', how='left')
        
        # Use aggregated review count if available, otherwise use original
        if 'review_count_agg' in self.df.columns:
            self.df['review_count'] = self.df['review_count_agg'].fillna(
                self.df.get('review_count', 0))
            self.df.drop('review_count_agg', axis=1, inplace=True)
        
        # Fill NaN for restaurants without reviews
        self.df['avg_review_rating'] = self.df['avg_review_rating'].fillna(self.df['rating'])
        self.df['rating_std'] = self.df['rating_std'].fillna(0)
        self.df['all_reviews_text'] = self.df['all_reviews_text'].fillna('')
    
    def build_model(self, weights=None, use_reviews=True, use_location=True):
        """Build content-based recommendation model"""
        if weights is None:
            weights = {
                'content': 0.35,
                'rating': 0.20,
                'price': 0.10,
                'reviews': 0.20,
                'location': 0.15
            }
        
        n_restaurants = len(self.df)
        
        # 1. Content-based similarity (TF-IDF on restaurant features)
        tfidf_content = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        content_matrix = tfidf_content.fit_transform(self.df['combined_features'])
        content_sim = cosine_similarity(content_matrix, content_matrix)
        
        # 2. Rating similarity
        ratings = self.df['rating'].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        ratings_scaled = scaler.fit_transform(ratings)
        rating_sim = 1 - np.abs(ratings_scaled - ratings_scaled.T)
        
        # 3. Price similarity
        price_levels = self.df['price_level'].fillna(2).values.reshape(-1, 1)
        price_scaled = price_levels / 4.0
        price_sim = 1 - np.abs(price_scaled - price_scaled.T)
        
        # 4. Review text similarity
        review_sim = np.zeros((n_restaurants, n_restaurants))
        if use_reviews and 'all_reviews_text' in self.df.columns:
            has_reviews = self.df['all_reviews_text'].str.len() > 0
            if has_reviews.sum() > 0:
                review_texts = self.df['all_reviews_text'].fillna('')
                tfidf_reviews = TfidfVectorizer(stop_words='english', max_features=100, min_df=1)
                try:
                    review_matrix = tfidf_reviews.fit_transform(review_texts)
                    review_sim = cosine_similarity(review_matrix, review_matrix)
                except:
                    print("Warning: Could not process review texts for similarity")
        
        # 5. Location similarity
        location_sim = np.zeros((n_restaurants, n_restaurants))
        if use_location and 'latitude' in self.df.columns and 'longitude' in self.df.columns:
            print("Calculating location-based similarities...")
            location_sim = self.calculate_distance_matrix()
            self.location_matrix = location_sim
        
        # Combine all similarities with weights
        self.similarity_matrix = (
            weights['content'] * content_sim +
            weights['rating'] * rating_sim +
            weights['price'] * price_sim +
            weights['reviews'] * review_sim +
            weights['location'] * location_sim
        )
        
        print(f"Model built successfully with {len(self.df)} restaurants!")
        return self
    
    def build_collaborative_filtering(self, method='user-based', n_factors=20):
        """Build collaborative filtering model"""
        print(f"\nBuilding collaborative filtering model ({method})...")
        
        # Create user-item matrix
        user_item_df = self.reviews.pivot_table(
            index='username',
            columns='place_id',
            values='rating',
            fill_value=0
        )
        
        self.user_item_matrix = user_item_df
        print(f"User-Item Matrix: {user_item_df.shape[0]} users × {user_item_df.shape[1]} items")
        
        if method == 'user-based':
            user_similarity = cosine_similarity(user_item_df.values)
            self.user_similarity_matrix = pd.DataFrame(
                user_similarity,
                index=user_item_df.index,
                columns=user_item_df.index
            )
            print(f"✓ User-based similarity matrix created")
            
        elif method == 'item-based':
            item_similarity = cosine_similarity(user_item_df.T.values)
            self.item_similarity_matrix = pd.DataFrame(
                item_similarity,
                index=user_item_df.columns,
                columns=user_item_df.columns
            )
            print(f"✓ Item-based similarity matrix created")
            
        elif method == 'matrix-factorization':
            user_item_matrix = user_item_df.values
            if user_item_matrix.shape[0] > n_factors and user_item_matrix.shape[1] > n_factors:
                sparse_matrix = csr_matrix(user_item_matrix)
                U, sigma, Vt = svds(sparse_matrix, k=min(n_factors, min(user_item_matrix.shape) - 1))
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
                print(f"✓ Matrix factorization model created with {n_factors} factors")
            else:
                print(f"⚠ Not enough data for matrix factorization. Using user-based instead.")
                return self.build_collaborative_filtering('user-based')
        
        return self
    
    def get_recommendations(self, restaurant_name, n=5, min_rating=None, 
                          price_level=None, cuisine_filter=None, 
                          county_filter=None, max_distance_km=None):
        """Get top N similar restaurants"""
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
            
            # Calculate distance from source restaurant
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
            if cuisine_filter and cuisine_filter.lower() not in str(restaurant['cuisine_type']).lower():
                continue
            if county_filter and county_filter.lower() not in str(restaurant['county']).lower():
                continue
            if max_distance_km and distance > max_distance_km:
                continue
                
            recommendations.append({
                'name': restaurant['name'],
                'cuisine': restaurant['cuisine_type'],
                'rating': restaurant['rating'],
                'review_count': restaurant['review_count'],
                'price_range': restaurant['price_range'],
                'atmosphere': restaurant['atmosphere'],
                'county': restaurant['county'],
                'address': restaurant['address'],
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
                            'rating': restaurant['rating'],
                            'review_count': restaurant['review_count'],
                            'price_range': restaurant['price_range'],
                            'predicted_rating': round(predicted_rating, 2),
                            'address': restaurant['address']
                        })
        
        recommendations = sorted(recommendations, key=lambda x: x['predicted_rating'], reverse=True)[:n]
        return pd.DataFrame(recommendations) if recommendations else "No recommendations found."
    
    def get_hybrid_recommendations(self, restaurant_name=None, username=None, 
                                  n=10, content_weight=0.5, collaborative_weight=0.5):
        """Hybrid recommendations combining content-based and collaborative filtering"""
        recommendations = {}
        
        # Get content-based recommendations
        if restaurant_name and self.similarity_matrix is not None:
            content_recs = self.get_recommendations(restaurant_name, n=n*2)
            if isinstance(content_recs, pd.DataFrame):
                for _, row in content_recs.iterrows():
                    name = row['name']
                    recommendations[name] = {
                        'name': name,
                        'cuisine': row['cuisine'],
                        'rating': row['rating'],
                        'content_score': row['similarity_score'] * content_weight,
                        'collaborative_score': 0,
                        'price_range': row['price_range'],
                        'address': row['address']
                    }
        
        # Get collaborative recommendations
        if username and self.user_similarity_matrix is not None:
            collab_recs = self.get_user_based_recommendations(username, n=n*2)
            if isinstance(collab_recs, pd.DataFrame):
                for _, row in collab_recs.iterrows():
                    name = row['name']
                    if name in recommendations:
                        recommendations[name]['collaborative_score'] = row['predicted_rating'] * collaborative_weight / 5.0
                    else:
                        recommendations[name] = {
                            'name': name,
                            'cuisine': row['cuisine_type'],
                            'rating': row['rating'],
                            'content_score': 0,
                            'collaborative_score': row['predicted_rating'] * collaborative_weight / 5.0,
                            'price_range': row['price_range'],
                            'address': row['address']
                        }
        
        # Calculate hybrid score
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
                    'restaurant': restaurant['name'],
                    'cuisine': restaurant['cuisine_type'],
                    'user_rating': review['rating'],
                    'avg_rating': restaurant['rating'],
                    'price_range': restaurant['price_range'],
                    'review_date': review['review_date']
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
        print(f"Cuisine: {restaurant['cuisine_type']}")
        print(f"Type: {restaurant['restaurant_type']}")
        print(f"Rating: {restaurant['rating']} ({restaurant['review_count']} reviews)")
        print(f"Price Range: {restaurant['price_range']}")
        print(f"Address: {restaurant['address']}")
        print(f"Atmosphere: {restaurant['atmosphere']}")
        print(f"Dietary Options: {restaurant['dietary_options']}")
        print(f"Service Options: {restaurant['service_options']}")
        
        if len(rest_reviews) > 0:
            print(f"\n--- Recent Reviews ---")
            for _, review in rest_reviews.head(5).iterrows():
                print(f"\n★ {review['rating']}/5 - {review['username']} ({review['review_date']})")
                print(f"   {review['review_text'][:200]}...")
        
        print(f"\n{'='*70}\n")
        return restaurant
    
    def get_top_rated(self, n=10, min_reviews=5):
        """Get top rated restaurants with minimum review count"""
        top = self.df[self.df['review_count'] >= min_reviews].nlargest(n, 'rating')
        return top[['name', 'cuisine_type', 'rating', 'review_count', 
                   'price_range', 'county', 'address']]
    
    def get_by_cuisine(self, cuisine, n=10, min_rating=None, service_option=None):
        """Get top restaurants by cuisine type"""
        filtered = self.df[self.df['cuisine_type'].str.contains(cuisine, case=False, na=False)]
        
        if min_rating:
            filtered = filtered[filtered['rating'] >= min_rating]
        
        if service_option:
            filtered = filtered[filtered['service_options'].str.contains(
                service_option, case=False, na=False)]
        
        return filtered.nlargest(n, 'rating')[['name', 'cuisine_type', 'rating', 
                                                'review_count', 'price_range', 
                                                'county', 'service_options', 
                                                'address', 'latitude', 'longitude']]
    
    def get_nearby_restaurants(self, latitude, longitude, radius_km=5, n=10, min_rating=None):
        """Find restaurants near a given location"""
        distances = []
        
        for idx, restaurant in self.df.iterrows():
            distance = self.haversine_distance(
                latitude, longitude,
                restaurant['latitude'],
                restaurant['longitude']
            )
            
            if distance <= radius_km:
                if min_rating is None or restaurant['rating'] >= min_rating:
                    distances.append({
                        'name': restaurant['name'],
                        'cuisine_type': restaurant['cuisine_type'],
                        'rating': restaurant['rating'],
                        'review_count': restaurant['review_count'],
                        'price_range': restaurant['price_range'],
                        'address': restaurant['address'],
                        'distance_km': round(distance, 2),
                        'latitude': restaurant['latitude'],
                        'longitude': restaurant['longitude']
                    })
        
        distances_df = pd.DataFrame(distances)
        if len(distances_df) > 0:
            distances_df = distances_df.sort_values('distance_km').head(n)
        
        return distances_df
    
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
                        'name': restaurant['name'],
                        'cuisine_type': restaurant['cuisine_type'],
                        'rating': restaurant['rating'],
                        'review_count': restaurant['review_count'],
                        'price_range': restaurant['price_range'],
                        'address': restaurant['address'],
                        'detour_km': round(detour, 2),
                        'distance_from_start_km': round(dist_from_start, 2),
                        'latitude': restaurant['latitude'],
                        'longitude': restaurant['longitude']
                    })
        
        route_df = pd.DataFrame(restaurants_on_route)
        if len(route_df) > 0:
            route_df = route_df.sort_values('detour_km')
        
        return route_df
    
    def get_all_cuisines(self):
        """Get list of all unique cuisines in the dataset"""
        cuisines = self.df['cuisine_type'].dropna().unique()
        return sorted(cuisines)
    
    def get_by_service_option(self, service_option, n=20, min_rating=None, 
                             cuisine=None, max_distance_km=None, 
                             center_lat=None, center_lon=None):
        """Find restaurants by service option (Dine-in, Takeaway, Delivery)"""
        filtered = self.df[self.df['service_options'].str.contains(
            service_option, case=False, na=False)]
        
        if min_rating:
            filtered = filtered[filtered['rating'] >= min_rating]
        
        if cuisine:
            filtered = filtered[filtered['cuisine_type'].str.contains(
                cuisine, case=False, na=False)]
        
        if max_distance_km and center_lat and center_lon:
            distances = []
            for idx, restaurant in filtered.iterrows():
                distance = self.haversine_distance(
                    center_lat, center_lon,
                    restaurant['latitude'],
                    restaurant['longitude']
                )
                if distance <= max_distance_km:
                    distances.append({
                        'index': idx,
                        'distance_km': round(distance, 2)
                    })
            
            if distances:
                dist_df = pd.DataFrame(distances).set_index('index')
                filtered = filtered.loc[dist_df.index].copy()
                filtered['distance_km'] = dist_df['distance_km'].values
                filtered = filtered.sort_values('distance_km')
        else:
            filtered = filtered.sort_values('rating', ascending=False)
        
        return filtered.head(n)[['name', 'cuisine_type', 'rating', 'review_count',
                                'price_range', 'service_options', 'county', 
                                'address', 'latitude', 'longitude']]
    
    def search_by_address(self, address_query, n=10):
        """Search restaurants by address (partial match)"""
        filtered = self.df[self.df['address'].str.contains(
            address_query, case=False, na=False)]
        
        return filtered.nlargest(n, 'rating')[['name', 'cuisine_type', 'rating',
                                               'review_count', 'price_range',
                                               'service_options', 'address',
                                               'latitude', 'longitude']]
    
    def get_cuisine_statistics(self):
        """Get statistics about cuisines in the dataset"""
        cuisine_stats = self.df.groupby('cuisine_type').agg({
            'name': 'count',
            'rating': 'mean',
            'review_count': 'sum'
        }).round(2)
        
        cuisine_stats.columns = ['restaurant_count', 'avg_rating', 'total_reviews']
        cuisine_stats = cuisine_stats.sort_values('restaurant_count', ascending=False)
        
        return cuisine_stats
    
    def get_service_options_summary(self):
        """Get summary of service options availability"""
        service_summary = {
            'Dine-in': len(self.df[self.df['service_options'].str.contains('Dine-in', case=False, na=False)]),
            'Takeaway': len(self.df[self.df['service_options'].str.contains('Takeaway', case=False, na=False)]),
            'Delivery': len(self.df[self.df['service_options'].str.contains('Delivery', case=False, na=False)])
        }
        return service_summary
    
    def search_restaurants(self, filters):
        """Advanced search with multiple filters"""
        filtered = self.df.copy()
        
        if 'min_rating' in filters:
            filtered = filtered[filtered['rating'] >= filters['min_rating']]
        if 'max_price_level' in filters:
            filtered = filtered[filtered['price_level'] <= filters['max_price_level']]
        if 'min_reviews' in filters:
            filtered = filtered[filtered['review_count'] >= filters['min_reviews']]
        if 'cuisine' in filters:
            filtered = filtered[filtered['cuisine_type'].str.contains(
                filters['cuisine'], case=False, na=False)]
        if 'county' in filters:
            filtered = filtered[filtered['county'].str.contains(
                filters['county'], case=False, na=False)]
        if 'dietary_options' in filters:
            filtered = filtered[filtered['dietary_options'].str.contains(
                filters['dietary_options'], case=False, na=False)]
        if 'service_options' in filters:
            filtered = filtered[filtered['service_options'].str.contains(
                filters['service_options'], case=False, na=False)]
        if 'atmosphere' in filters:
            filtered = filtered[filtered['atmosphere'].str.contains(
                filters['atmosphere'], case=False, na=False)]
        
        return filtered[['name', 'cuisine_type', 'rating', 'review_count',
                        'price_range', 'atmosphere', 'service_options', 'county', 'address',
                        'latitude', 'longitude']].sort_values('rating', ascending=False)
    
    def save_model(self, filepath='restaurant_recommender.pkl'):
        """Save the trained model to a pickle file"""
        model_data = {
            'df': self.df,
            'reviews': self.reviews,
            'similarity_matrix': self.similarity_matrix,
            'review_sentiment_scores': self.review_sentiment_scores,
            'user_item_matrix': self.user_item_matrix,
            'user_similarity_matrix': self.user_similarity_matrix,
            'item_similarity_matrix': getattr(self, 'item_similarity_matrix', None),
            'svd_model': self.svd_model,
            'location_matrix': self.location_matrix
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved successfully to: {filepath}")
        print(f"  File size: {os.path.getsize(filepath) / (1024*1024):.2f} MB")
    
    @classmethod
    def load_model(cls, filepath='restaurant_recommender.pkl'):
        """Load a trained model from a pickle file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        recommender = cls.__new__(cls)
        recommender.df = model_data['df']
        recommender.reviews = model_data['reviews']
        recommender.similarity_matrix = model_data['similarity_matrix']
        recommender.review_sentiment_scores = model_data.get('review_sentiment_scores')
        recommender.user_item_matrix = model_data.get('user_item_matrix')
        recommender.user_similarity_matrix = model_data.get('user_similarity_matrix')
        recommender.item_similarity_matrix = model_data.get('item_similarity_matrix')
        recommender.svd_model = model_data.get('svd_model')
        recommender.location_matrix = model_data.get('location_matrix')
        
        print(f"✓ Model loaded successfully from: {filepath}")
        print(f"  Restaurants: {len(recommender.df)}")
        print(f"  Reviews: {len(recommender.reviews)}")
        
        return recommender


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    print("="*70)
    print("BUILDING NEW MODEL")
    print("="*70)
    
    restaurants_path = r"C:\Users\Vishva\Downloads\Final_updated_restaurant_data.csv"
    reviews_path = r"C:\Users\Vishva\Downloads\Final_updated_userReviewsData.csv"
    model_save_path = r"C:\Users\Vishva\Downloads\restaurant_model.pkl"
    
    recommender = RestaurantRecommender(
        restaurants_file=restaurants_path,
        reviews_file=reviews_path
    )
    
    print("\nBuilding recommendation model...")
    recommender.preprocess_data().build_model()
    
    print("\nBuilding collaborative filtering...")
    recommender.build_collaborative_filtering(method='user-based')
    
    recommender.save_model(model_save_path)
    
    print("\n" + "="*70)
    print("MODEL SAVED! You can now load it anytime without rebuilding")
    print("="*70)
    
    print("\n" + "="*70)
    print("RESTAURANT RECOMMENDATION SYSTEM - READY!")
    print("="*70)
    
    # Example 1: Get similar restaurants
    print("\n\n1. Restaurants similar to 'The Garden Cafe':")
    print("-"*70)
    recommendations = recommender.get_recommendations('The Garden Cafe', n=5)
    if isinstance(recommendations, pd.DataFrame):
        print(recommendations[['name', 'cuisine', 'rating', 'distance_km', 'similarity_score']].to_string(index=False))
    else:
        print(recommendations)
    
    # Example 2: Similar restaurants with distance filter
    print("\n\n2. Similar restaurants (min rating 4.5, within 5km):")
    print("-"*70)
    filtered_recs = recommender.get_recommendations('The Garden Cafe', n=5, min_rating=4.5, max_distance_km=5)
    if isinstance(filtered_recs, pd.DataFrame):
        print(filtered_recs[['name', 'rating', 'distance_km', 'similarity_score']].to_string(index=False))
    else:
        print(filtered_recs)
    
    # Example 3: Restaurant details
    print("\n\n3. Detailed information:")
    print("-"*70)
    recommender.get_restaurant_details('The Garden Cafe')
    
    # Example 4: Nearby restaurants
    print("\n\n4. Restaurants near The Garden Cafe (within 3km):")
    print("-"*70)
    garden_cafe = recommender.df[recommender.df['name'] == 'The Garden Cafe'].iloc[0]
    nearby = recommender.get_nearby_restaurants(
        garden_cafe['latitude'], 
        garden_cafe['longitude'], 
        radius_km=3,
        n=5,
        min_rating=4.0
    )
    print(nearby[['name', 'rating', 'distance_km', 'address']].to_string(index=False))
    
    # Example 5: Restaurants along route
    print("\n\n5. Restaurants between two points (along route):")
    print("-"*70)
    start_lat, start_lon = 51.91124, -8.47154
    end_lat, end_lon = 51.8985, -8.4756
    
    on_route = recommender.get_restaurants_between_points(
        start_lat, start_lon, end_lat, end_lon,
        max_detour_km=1.5, min_rating=4.5
    )
    if len(on_route) > 0:
        print(on_route.head(5)[['name', 'rating', 'detour_km', 'distance_from_start_km']].to_string(index=False))
    
    # Example 6: Top rated
    print("\n\n6. Top 5 rated restaurants (min 10 reviews):")
    print("-"*70)
    top = recommender.get_top_rated(n=5, min_reviews=10)
    print(top[['name', 'cuisine_type', 'rating', 'review_count']].to_string(index=False))
    
    # Example 7: By cuisine
    print("\n\n7. Top Irish cuisine restaurants:")
    print("-"*70)
    irish = recommender.get_by_cuisine('Irish', n=5)
    print(irish[['name', 'cuisine_type', 'rating', 'service_options']].to_string(index=False))
    
    # Example 8: By service option
    print("\n\n8. Restaurants offering DELIVERY:")
    print("-"*70)
    delivery = recommender.get_by_service_option('Delivery', n=5, min_rating=4.5)
    print(delivery[['name', 'cuisine_type', 'rating', 'service_options']].to_string(index=False))
    
    # Example 9: Search by address
    print("\n\n9. Restaurants in 'Blackpool' area:")
    print("-"*70)
    blackpool = recommender.search_by_address('Blackpool', n=5)
    print(blackpool[['name', 'rating', 'address']].to_string(index=False))
    
    # Example 10: All cuisines
    print("\n\n10. All available cuisines:")
    print("-"*70)
    cuisines = recommender.get_all_cuisines()
    print(f"Total cuisines: {len(cuisines)}")
    print("Sample cuisines:", cuisines[:10])
    
    # Example 11: Service summary
    print("\n\n11. Service options availability:")
    print("-"*70)
    service_summary = recommender.get_service_options_summary()
    for service, count in service_summary.items():
        print(f"  {service}: {count} restaurants")
    
    # Example 12: Cuisine statistics
    print("\n\n12. Top 5 cuisines by restaurant count:")
    print("-"*70)
    cuisine_stats = recommender.get_cuisine_statistics()
    print(cuisine_stats.head(5).to_string())
    
    # Example 13: Advanced search
    print("\n\n13. Advanced search (Rating 4.5+, Delivery, Cork):")
    print("-"*70)
    filters = {
        'min_rating': 4.5,
        'max_price_level': 2,
        'county': 'Cork',
        'min_reviews': 5,
        'service_options': 'Delivery'
    }
    results = recommender.search_restaurants(filters)
    print(results.head(5)[['name', 'cuisine_type', 'rating', 'service_options']].to_string(index=False))
    
    # COLLABORATIVE FILTERING EXAMPLES
    print("\n\n" + "="*70)
    print("COLLABORATIVE FILTERING RECOMMENDATIONS")
    print("="*70)
    
    if recommender.user_similarity_matrix is not None:
        # Find a user with multiple reviews for better demonstration
        user_review_counts = recommender.reviews.groupby('username').size().sort_values(ascending=False)
        
        print("\n\n14. Top active users:")
        print("-"*70)
        print(user_review_counts.head(10).to_string())
        
        # Use a user with multiple reviews
        sample_user = user_review_counts.index[0]  # Most active user
        
        # Example 15: User-based recommendations
        print(f"\n\n15. User-based recommendations for '{sample_user}':")
        print("-"*70)
        user_recs = recommender.get_user_based_recommendations(sample_user, n=5, min_rating=3.5)
        if isinstance(user_recs, pd.DataFrame):
            print(user_recs[['name', 'cuisine_type', 'rating', 'predicted_rating']].to_string(index=False))
        else:
            print(user_recs)
        
        # Example 16: User preferences
        print(f"\n\n16. User preferences for '{sample_user}':")
        print("-"*70)
        user_prefs = recommender.get_user_preferences(sample_user)
        if isinstance(user_prefs, dict):
            print(f"Total reviews: {user_prefs['total_reviews']}")
            print(f"Average rating given: {user_prefs['avg_rating_given']:.1f}")
            print(f"Favorite cuisines: {user_prefs['favorite_cuisines']}")
            print(f"\nTop rated by user:")
            print(user_prefs['reviews'].head(5)[['restaurant', 'cuisine', 'user_rating']].to_string(index=False))
        
        # Example 17: Users who liked restaurant
        print("\n\n17. Users who liked 'The Garden Cafe':")
        print("-"*70)
        users_who_liked = recommender.get_users_who_liked_restaurant('The Garden Cafe', min_rating=4)
        if isinstance(users_who_liked, pd.DataFrame):
            print(users_who_liked.head(5)[['username', 'rating', 'review_date']].to_string(index=False))
        
        # Example 18: Hybrid recommendations with active user
        print(f"\n\n18. HYBRID recommendations for '{sample_user}' based on 'The Garden Cafe':")
        print("-"*70)
        hybrid_recs = recommender.get_hybrid_recommendations(
            restaurant_name='The Garden Cafe',
            username=sample_user,
            n=5,
            content_weight=0.6,
            collaborative_weight=0.4
        )
        if isinstance(hybrid_recs, pd.DataFrame):
            print(hybrid_recs[['name', 'rating', 'content_score', 'collaborative_score', 'hybrid_score']].to_string(index=False))
        
        # Example 19: Compare different users
        print("\n\n19. Comparison - Collaborative filtering for different user types:")
        print("-"*70)
        
        # User with few reviews
        few_review_user = user_review_counts[user_review_counts == 1].index[0] if len(user_review_counts[user_review_counts == 1]) > 0 else None
        if few_review_user:
            print(f"\nUser with 1 review ('{few_review_user}'):")
            recs_few = recommender.get_user_based_recommendations(few_review_user, n=3, min_rating=3.5)
            if isinstance(recs_few, pd.DataFrame):
                print(f"  Found {len(recs_few)} recommendations")
            else:
                print(f"  {recs_few}")
        
        # User with many reviews
        many_review_user = user_review_counts.index[0]
        print(f"\nUser with {user_review_counts.iloc[0]} reviews ('{many_review_user}'):")
        recs_many = recommender.get_user_based_recommendations(many_review_user, n=3, min_rating=3.5)
        if isinstance(recs_many, pd.DataFrame):
            print(f"  Found {len(recs_many)} recommendations")
            print(recs_many[['name', 'predicted_rating']].to_string(index=False))
        
    else:
        print("\n⚠ Collaborative filtering not built in this run.")
    
    print("\n" + "="*70)
    print("System ready for recommendations!")
    print("="*70)