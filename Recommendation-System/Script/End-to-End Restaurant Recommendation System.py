"""
COMPLETE END-TO-END RESTAURANT RECOMMENDATION SYSTEM
====================================================

Architecture:
1. Frontend Form (HTML/React) → User Preferences
2. Backend API (Flask) → Process Preferences  
3. ML Model (Pickle) → Get Recommendations (returns place_ids)
4. Database (SQLite/PostgreSQL) → Retrieve Full Details
5. Response → Send Complete Data to Frontend

This file contains:
- Database setup and management
- Flask API with all endpoints
- Integration between Model and Database
- Sample HTML frontend
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

# Import your recommender
from resturant_mo_3 import RestaurantRecommender

# ============================================================================
# 1. DATABASE SETUP
# ============================================================================

class RestaurantDatabase:
    """Handle all database operations"""
    
    def __init__(self, db_path='restaurant_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database from CSV files"""
        print("Initializing database...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create restaurants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                place_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                restaurant_type TEXT,
                cuisine_type TEXT,
                address TEXT,
                county TEXT,
                rating REAL,
                review_count INTEGER,
                latitude REAL,
                longitude REAL,
                price_range TEXT,
                price_level INTEGER,
                price_min INTEGER,
                price_max INTEGER,
                phone TEXT,
                website TEXT,
                url TEXT,
                atmosphere TEXT,
                dietary_options TEXT,
                service_options TEXT,
                amenities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                place_id INTEGER,
                restaurant_name TEXT,
                username TEXT,
                user_review_id INTEGER,
                review_date TEXT,
                rating REAL,
                review_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (place_id) REFERENCES restaurants (place_id)
            )
        ''')
        
        # Create user preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_address TEXT,
                cuisine_preference TEXT,
                dietary_preference TEXT,
                service_preference TEXT,
                atmosphere_preference TEXT,
                price_level INTEGER,
                max_distance_km REAL,
                min_rating REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create recommendation logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendation_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                place_ids TEXT,
                filters_applied TEXT,
                result_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✓ Database initialized")
    
    def load_data_from_csv(self, restaurants_csv, reviews_csv):
        """Load data from CSV files into database"""
        print("Loading data from CSV files...")
        
        conn = self.get_connection()
        
        # Load restaurants
        restaurants_df = pd.read_csv(restaurants_csv)
        restaurants_df.to_sql('restaurants', conn, if_exists='replace', index=False)
        print(f"✓ Loaded {len(restaurants_df)} restaurants")
        
        # Load reviews
        reviews_df = pd.read_csv(reviews_csv)
        reviews_df.to_sql('reviews', conn, if_exists='replace', index=False)
        print(f"✓ Loaded {len(reviews_df)} reviews")
        
        conn.close()
    
    def get_restaurant_by_place_id(self, place_id):
        """Get complete restaurant details by place_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM restaurants WHERE place_id = ?
        ''', (place_id,))
        
        restaurant = cursor.fetchone()
        conn.close()
        
        if restaurant:
            return dict(restaurant)
        return None
    
    def get_restaurants_by_place_ids(self, place_ids):
        """Get multiple restaurants by place_ids"""
        if not place_ids:
            return []
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(place_ids))
        cursor.execute(f'''
            SELECT * FROM restaurants WHERE place_id IN ({placeholders})
        ''', place_ids)
        
        restaurants = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in restaurants]
    
    def get_reviews_by_place_id(self, place_id, limit=10):
        """Get reviews for a restaurant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reviews 
            WHERE place_id = ? 
            ORDER BY rating DESC, created_at DESC
            LIMIT ?
        ''', (place_id, limit))
        
        reviews = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in reviews]
    
    def save_user_preferences(self, preferences, session_id):
        """Save user preferences"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_preferences 
            (session_id, user_address, cuisine_preference, dietary_preference,
             service_preference, atmosphere_preference, price_level, 
             max_distance_km, min_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            preferences.get('address'),
            preferences.get('cuisine'),
            preferences.get('dietary'),
            preferences.get('service'),
            preferences.get('atmosphere'),
            preferences.get('price_level'),
            preferences.get('max_distance_km'),
            preferences.get('min_rating')
        ))
        
        conn.commit()
        conn.close()
    
    def log_recommendation(self, session_id, place_ids, filters, count):
        """Log recommendation request"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recommendation_logs 
            (session_id, place_ids, filters_applied, result_count)
            VALUES (?, ?, ?, ?)
        ''', (
            session_id,
            json.dumps(place_ids),
            json.dumps(filters),
            count
        ))
        
        conn.commit()
        conn.close()


# ============================================================================
# 2. FLASK API APPLICATION
# ============================================================================

app = Flask(__name__)
CORS(app)

# Initialize components
MODEL_PATH = 'restaurant_model.pkl'
DB_PATH = 'restaurant_data.db'

print("="*80)
print("INITIALIZING RESTAURANT RECOMMENDATION SYSTEM")
print("="*80)

# Initialize database
db = RestaurantDatabase(DB_PATH)

# Load model
print(f"\nLoading ML model from {MODEL_PATH}...")
recommender = RestaurantRecommender.load_model(MODEL_PATH)
print("✓ Model loaded successfully")

# Check if database is empty and load from CSV if needed
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM restaurants")
count = cursor.fetchone()[0]
conn.close()

if count == 0:
    print("\n⚠ Database is empty. Loading data from CSV...")
    db.load_data_from_csv(
        'Final_updated_restaurant_data.csv',
        'Final_updated_userReviewsData.csv'
    )

print("\n✓ System ready!")
print("="*80 + "\n")


# ============================================================================
# 3. API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve the user preference form"""
    return render_template_string(USER_PREFERENCE_FORM_HTML)


@app.route('/api/preferences/options', methods=['GET'])
def get_preference_options():
    """
    Get all available options for the preference form
    Returns: Lists of cuisines, dietary options, services, etc.
    """
    cuisines = recommender.get_all_cuisines()
    service_summary = recommender.get_service_options_summary()
    
    # Get unique values from database
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT dietary_options FROM restaurants WHERE dietary_options != 'None'")
    dietary_options = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT atmosphere FROM restaurants WHERE atmosphere != 'General'")
    atmospheres = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'cuisines': list(cuisines),
        'dietary_options': dietary_options,
        'service_options': list(service_summary.keys()),
        'atmospheres': atmospheres,
        'price_levels': [
            {'value': 1, 'label': '€ - Budget (€5-15)'},
            {'value': 2, 'label': '€€ - Moderate (€10-25)'},
            {'value': 3, 'label': '€€€ - Expensive (€20-40)'},
            {'value': 4, 'label': '€€€€ - Fine Dining (€35+)'}
        ]
    })


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Main endpoint: Get personalized restaurant recommendations
    
    Request body:
    {
        "address": "Patrick Street, Cork",
        "cuisine": "Italian",
        "dietary": "Vegetarian",
        "service": "Delivery",
        "atmosphere": "Casual",
        "price_level": 2,
        "max_distance_km": 5,
        "min_rating": 4.0,
        "limit": 10
    }
    
    Response:
    {
        "session_id": "abc123",
        "user_location": {...},
        "filters_applied": {...},
        "count": 10,
        "recommendations": [
            {
                "place_id": 1,
                "name": "The Garden Cafe",
                "full_details": {...},
                "reviews": [...]
            }
        ]
    }
    """
    import uuid
    
    data = request.json
    session_id = str(uuid.uuid4())
    
    # Extract preferences
    user_address = data.get('address')
    cuisine = data.get('cuisine')
    dietary = data.get('dietary')
    service = data.get('service')
    atmosphere = data.get('atmosphere')
    price_level = data.get('price_level')
    max_distance_km = data.get('max_distance_km', 5)
    min_rating = data.get('min_rating', 4.0)
    limit = data.get('limit', 10)
    
    # Validate required fields
    if not user_address:
        return jsonify({'error': 'Address is required'}), 400
    
    # Save user preferences to database
    db.save_user_preferences(data, session_id)
    
    try:
        # STEP 1: Get recommendations from ML model
        print(f"\n{'='*60}")
        print(f"Processing recommendation request (Session: {session_id[:8]}...)")
        print(f"{'='*60}")
        
        model_results = recommender.get_restaurants_by_user_address(
            user_address=user_address,
            radius_km=max_distance_km,
            n=limit * 2,  # Get extra for filtering
            min_rating=min_rating,
            cuisine_filter=cuisine,
            service_filter=service
        )
        
        if isinstance(model_results, str):
            # Error from model
            return jsonify({'error': model_results}), 404
        
        # STEP 2: Extract place_ids from model results
        place_ids = model_results['place_id'].tolist() if 'place_id' in model_results.columns else []
        
        if not place_ids:
            return jsonify({
                'message': 'No restaurants found matching your preferences',
                'session_id': session_id
            }), 404
        
        print(f"✓ Model returned {len(place_ids)} place_ids")
        
        # STEP 3: Get complete details from database
        print(f"✓ Fetching details from database...")
        restaurants_details = []
        
        for place_id in place_ids[:limit]:
            # Get restaurant details
            restaurant = db.get_restaurant_by_place_id(place_id)
            
            if restaurant:
                # Apply additional filters
                if dietary and dietary not in str(restaurant.get('dietary_options', '')):
                    continue
                if atmosphere and atmosphere not in str(restaurant.get('atmosphere', '')):
                    continue
                if price_level and restaurant.get('price_level') != price_level:
                    continue
                
                # Get reviews
                reviews = db.get_reviews_by_place_id(place_id, limit=5)
                
                # Get distance from model results
                model_row = model_results[model_results['place_id'] == place_id]
                distance_km = model_row['distance_km'].values[0] if len(model_row) > 0 else None
                
                # Combine all data
                restaurants_details.append({
                    'place_id': place_id,
                    'name': restaurant['name'],
                    'restaurant_type': restaurant['restaurant_type'],
                    'cuisine_type': restaurant['cuisine_type'],
                    'rating': restaurant['rating'],
                    'review_count': restaurant['review_count'],
                    'distance_km': distance_km,
                    'price_range': restaurant['price_range'],
                    'price_level': restaurant['price_level'],
                    'address': restaurant['address'],
                    'phone': restaurant['phone'],
                    'website': restaurant['website'],
                    'latitude': restaurant['latitude'],
                    'longitude': restaurant['longitude'],
                    'atmosphere': restaurant['atmosphere'],
                    'dietary_options': restaurant['dietary_options'],
                    'service_options': restaurant['service_options'],
                    'amenities': restaurant['amenities'],
                    'reviews': reviews,
                    'review_sample': reviews[0] if reviews else None
                })
        
        print(f"✓ Retrieved {len(restaurants_details)} complete restaurant details")
        
        # STEP 4: Log the recommendation
        db.log_recommendation(
            session_id=session_id,
            place_ids=place_ids[:limit],
            filters=data,
            count=len(restaurants_details)
        )
        
        # Get user location info
        geo_result = recommender.geocode_address(user_address)
        
        # STEP 5: Return complete response
        response = {
            'session_id': session_id,
            'user_location': {
                'address': geo_result.get('formatted_address', user_address),
                'latitude': geo_result.get('latitude'),
                'longitude': geo_result.get('longitude')
            },
            'filters_applied': {
                'cuisine': cuisine,
                'dietary': dietary,
                'service': service,
                'atmosphere': atmosphere,
                'price_level': price_level,
                'max_distance_km': max_distance_km,
                'min_rating': min_rating
            },
            'count': len(restaurants_details),
            'recommendations': restaurants_details
        }
        
        print(f"✓ Sending {len(restaurants_details)} recommendations to frontend")
        print(f"{'='*60}\n")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/api/restaurant/<int:place_id>', methods=['GET'])
def get_restaurant_details(place_id):
    """Get complete details for a specific restaurant"""
    restaurant = db.get_restaurant_by_place_id(place_id)
    
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    reviews = db.get_reviews_by_place_id(place_id, limit=20)
    
    return jsonify({
        'restaurant': restaurant,
        'reviews': reviews,
        'review_count': len(reviews)
    })


@app.route('/api/similar/<int:place_id>', methods=['GET'])
def get_similar_restaurants(place_id):
    """Get similar restaurants based on a place_id"""
    # Get restaurant name
    restaurant = db.get_restaurant_by_place_id(place_id)
    
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    # Get similar from model
    similar = recommender.get_recommendations(
        restaurant_name=restaurant['name'],
        n=10
    )
    
    if isinstance(similar, str):
        return jsonify({'error': similar}), 404
    
    # Get full details from database
    place_ids = similar['place_id'].tolist() if 'place_id' in similar.columns else []
    similar_details = db.get_restaurants_by_place_ids(place_ids)
    
    return jsonify({
        'source_restaurant': restaurant,
        'similar_count': len(similar_details),
        'similar_restaurants': similar_details
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM restaurants")
    restaurant_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reviews")
    review_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'model': 'loaded',
        'restaurants': restaurant_count,
        'reviews': review_count
    })


# ============================================================================
# 4. USER PREFERENCE FORM HTML
# ============================================================================

USER_PREFERENCE_FORM_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Find Your Perfect Restaurant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .form-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }
        
        .form-section {
            margin-bottom: 30px;
        }
        
        .form-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        
        .restaurant-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .restaurant-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .restaurant-header {
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }
        
        .restaurant-name {
            font-size: 1.4em;
            color: #333;
            margin-bottom: 5px;
        }
        
        .restaurant-cuisine {
            color: #667eea;
            font-weight: 600;
        }
        
        .restaurant-info {
            margin: 10px 0;
        }
        
        .info-row {
            display: flex;
            align-items: center;
            margin: 8px 0;
            color: #666;
        }
        
        .info-row strong {
            color: #333;
            margin-right: 5px;
        }
        
        .rating {
            background: #fbbf24;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
        }
        
        .distance {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            margin-left: 10px;
        }
        
        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }
        
        .tag {
            background: #f3f4f6;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            color: #666;
        }
        
        .view-details-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            margin-top: 15px;
            font-weight: 600;
        }
        
        .no-results {
            text-align: center;
            padding: 60px;
            color: white;
            font-size: 1.2em;
        }
        
        .error-message {
            background: #fef2f2;
            color: #dc2626;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #dc2626;
        }
        
        .success-message {
            background: #f0fdf4;
            color: #16a34a;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #16a34a;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽️ Find Your Perfect Restaurant</h1>
            <p>Tell us your preferences, and we'll recommend the best spots in Cork</p>
        </div>
        
        <div class="form-card">
            <form id="preferenceForm">
                <div class="form-section">
                    <h3>📍 Location</h3>
                    <div class="form-group">
                        <label for="address">Your Address or Location</label>
                        <input type="text" id="address" name="address" 
                               placeholder="e.g., Patrick Street, Cork or Blackpool, Cork" 
                               required>
                    </div>
                    <div class="form-group">
                        <label for="max_distance">Maximum Distance (km)</label>
                        <input type="number" id="max_distance" name="max_distance" 
                               value="5" min="1" max="50" step="0.5">
                    </div>
                </div>
                
                <div class="form-section">
                    <h3>🍴 Food Preferences</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="cuisine">Cuisine Type (Optional)</label>
                            <select id="cuisine" name="cuisine">
                                <option value="">Any Cuisine</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="dietary">Dietary Preference (Optional)</label>
                            <select id="dietary" name="dietary">
                                <option value="">No Preference</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3>⭐ Restaurant Features</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="service">Service Type (Optional)</label>
                            <select id="service" name="service">
                                <option value="">Any Service</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="atmosphere">Atmosphere (Optional)</label>
                            <select id="atmosphere" name="atmosphere">
                                <option value="">Any Atmosphere</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="price_level">Price Range</label>
                            <select id="price_level" name="price_level">
                                <option value="">Any Price</option>
                                <option value="1">€ - Budget (€5-15)</option>
                                <option value="2">€€ - Moderate (€10-25)</option>
                                <option value="3">€€€ - Expensive (€20-40)</option>
                                <option value="4">€€€€ - Fine Dining (€35+)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="min_rating">Minimum Rating</label>
                            <select id="min_rating" name="min_rating">
                                <option value="0">Any Rating</option>
                                <option value="3.5">3.5+ Stars</option>
                                <option value="4.0" selected>4.0+ Stars</option>
                                <option value="4.5">4.5+ Stars</option>
                                <option value="4.8">4.8+ Stars</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <button type="submit" id="submitBtn">
                    Find Restaurants
                </button>
            </form>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        // Load form options on page load
        async function loadFormOptions() {
            try {
                const response = await fetch('/api/preferences/options');
                const options = await response.json();
                
                // Populate cuisines
                const cuisineSelect = document.getElementById('cuisine');
                options.cuisines.forEach(cuisine => {
                    const option = document.createElement('option');
                    option.value = cuisine;
                    option.textContent = cuisine;
                    cuisineSelect.appendChild(option);
                });
                
                // Populate dietary options
                const dietarySelect = document.getElementById('dietary');
                options.dietary_options.forEach(dietary => {
                    const option = document.createElement('option');
                    option.value = dietary;
                    option.textContent = dietary;
                    dietarySelect.appendChild(option);
                });
                
                // Populate service options
                const serviceSelect = document.getElementById('service');
                options.service_options.forEach(service => {
                    const option = document.createElement('option');
                    option.value = service;
                    option.textContent = service;
                    serviceSelect.appendChild(option);
                });
                
                // Populate atmospheres
                const atmosphereSelect = document.getElementById('atmosphere');
                options.atmospheres.forEach(atmosphere => {
                    const option = document.createElement('option');
                    option.value = atmosphere;
                    option.textContent = atmosphere;
                    atmosphereSelect.appendChild(option);
                });
                
            } catch (error) {
                console.error('Error loading options:', error);
            }
        }
        
        // Handle form submission
        document.getElementById('preferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const resultsDiv = document.getElementById('results');
            
            // Disable submit button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Searching...';
            
            // Show loading
            resultsDiv.innerHTML = `
                <div class="form-card loading">
                    <div class="loading-spinner"></div>
                    <h3>Finding the perfect restaurants for you...</h3>
                    <p>Analyzing your preferences and location</p>
                </div>
            `;
            
            // Collect form data
            const formData = {
                address: document.getElementById('address').value,
                cuisine: document.getElementById('cuisine').value || null,
                dietary: document.getElementById('dietary').value || null,
                service: document.getElementById('service').value || null,
                atmosphere: document.getElementById('atmosphere').value || null,
                price_level: document.getElementById('price_level').value ? 
                    parseInt(document.getElementById('price_level').value) : null,
                max_distance_km: parseFloat(document.getElementById('max_distance').value),
                min_rating: parseFloat(document.getElementById('min_rating').value),
                limit: 12
            };
            
            try {
                const response = await fetch('/api/recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayResults(data);
                } else {
                    displayError(data.error || 'An error occurred');
                }
                
            } catch (error) {
                displayError('Network error: ' + error.message);
            } finally {
                // Re-enable submit button
                submitBtn.disabled = false;
                submitBtn.textContent = 'Find Restaurants';
            }
        });
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            
            if (data.count === 0) {
                resultsDiv.innerHTML = `
                    <div class="no-results">
                        <h2>😕 No restaurants found</h2>
                        <p>Try adjusting your filters or increasing the search radius</p>
                    </div>
                `;
                return;
            }
            
            let html = `
                <div class="form-card">
                    <div class="success-message">
                        ✓ Found ${data.count} restaurants near ${data.user_location.address}
                    </div>
                    <h2 style="margin-bottom: 10px;">Your Personalized Recommendations</h2>
                    <p style="color: #666; margin-bottom: 20px;">
                        Based on your preferences: 
                        ${data.filters_applied.cuisine ? data.filters_applied.cuisine + ' cuisine, ' : ''}
                        ${data.filters_applied.dietary ? data.filters_applied.dietary + ' options, ' : ''}
                        ${data.filters_applied.service ? data.filters_applied.service + ' service, ' : ''}
                        within ${data.filters_applied.max_distance_km}km
                    </p>
                </div>
                
                <div class="results-grid">
            `;
            
            data.recommendations.forEach(restaurant => {
                html += `
                    <div class="restaurant-card">
                        <div class="restaurant-header">
                            <h3 class="restaurant-name">${restaurant.name}</h3>
                            <p class="restaurant-cuisine">${restaurant.cuisine_type}</p>
                        </div>
                        
                        <div class="restaurant-info">
                            <div class="info-row">
                                <span class="rating">⭐ ${restaurant.rating}</span>
                                <span class="distance">📍 ${restaurant.distance_km} km</span>
                            </div>
                            
                            <div class="info-row">
                                <strong>Price:</strong> ${restaurant.price_range}
                            </div>
                            
                            <div class="info-row">
                                <strong>Type:</strong> ${restaurant.restaurant_type}
                            </div>
                            
                            <div class="info-row">
                                <strong>Address:</strong> ${restaurant.address}
                            </div>
                            
                            ${restaurant.phone ? `
                                <div class="info-row">
                                    <strong>Phone:</strong> ${restaurant.phone}
                                </div>
                            ` : ''}
                            
                            <div class="tags">
                                ${restaurant.atmosphere ? `<span class="tag">${restaurant.atmosphere}</span>` : ''}
                                ${restaurant.dietary_options ? `<span class="tag">${restaurant.dietary_options}</span>` : ''}
                                ${restaurant.service_options ? 
                                    restaurant.service_options.split(',').map(s => 
                                        `<span class="tag">${s.trim()}</span>`
                                    ).join('') : ''}
                            </div>
                            
                            ${restaurant.review_sample ? `
                                <div style="margin-top: 15px; padding: 10px; background: #f9fafb; border-radius: 8px;">
                                    <strong>Recent Review:</strong>
                                    <p style="margin-top: 5px; color: #666; font-size: 0.9em;">
                                        "${restaurant.review_sample.review_text.substring(0, 100)}..."
                                    </p>
                                    <p style="margin-top: 5px; font-size: 0.85em; color: #999;">
                                        - ${restaurant.review_sample.username}
                                    </p>
                                </div>
                            ` : ''}
                        </div>
                        
                        <button class="view-details-btn" onclick="viewDetails(${restaurant.place_id})">
                            View Full Details
                        </button>
                    </div>
                `;
            });
            
            html += '</div>';
            resultsDiv.innerHTML = html;
            
            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
        
        function displayError(message) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="form-card">
                    <div class="error-message">
                        <strong>Error:</strong> ${message}
                    </div>
                </div>
            `;
        }
        
        async function viewDetails(placeId) {
            try {
                const response = await fetch(`/api/restaurant/${placeId}`);
                const data = await response.json();
                
                if (response.ok) {
                    showRestaurantModal(data);
                }
            } catch (error) {
                alert('Error loading details: ' + error.message);
            }
        }
        
        function showRestaurantModal(data) {
            const restaurant = data.restaurant;
            const reviews = data.reviews;
            
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                padding: 20px;
            `;
            
            modal.innerHTML = `
                <div style="background: white; border-radius: 20px; max-width: 800px; max-height: 90vh; overflow-y: auto; padding: 40px;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                        <div>
                            <h2 style="color: #667eea; margin-bottom: 5px;">${restaurant.name}</h2>
                            <p style="color: #666;">${restaurant.cuisine_type}</p>
                        </div>
                        <button onclick="this.closest('div[style*=fixed]').remove()" 
                                style="background: #f3f4f6; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 20px;">
                            ✕
                        </button>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div>
                            <strong>Rating:</strong> ⭐ ${restaurant.rating} (${restaurant.review_count} reviews)
                        </div>
                        <div>
                            <strong>Price:</strong> ${restaurant.price_range}
                        </div>
                        <div>
                            <strong>Type:</strong> ${restaurant.restaurant_type}
                        </div>
                        <div>
                            <strong>Atmosphere:</strong> ${restaurant.atmosphere}
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <strong>Address:</strong><br>
                        ${restaurant.address}
                    </div>
                    
                    ${restaurant.phone ? `
                        <div style="margin-bottom: 20px;">
                            <strong>Phone:</strong> ${restaurant.phone}
                        </div>
                    ` : ''}
                    
                    ${restaurant.website ? `
                        <div style="margin-bottom: 20px;">
                            <strong>Website:</strong> <a href="${restaurant.website}" target="_blank" style="color: #667eea;">Visit Website</a>
                        </div>
                    ` : ''}
                    
                    <div style="margin-bottom: 20px;">
                        <strong>Services:</strong><br>
                        ${restaurant.service_options}
                    </div>
                    
                    ${restaurant.dietary_options ? `
                        <div style="margin-bottom: 20px;">
                            <strong>Dietary Options:</strong> ${restaurant.dietary_options}
                        </div>
                    ` : ''}
                    
                    ${restaurant.amenities ? `
                        <div style="margin-bottom: 20px;">
                            <strong>Amenities:</strong> ${restaurant.amenities}
                        </div>
                    ` : ''}
                    
                    <div style="margin-top: 30px;">
                        <h3 style="color: #667eea; margin-bottom: 15px;">Customer Reviews</h3>
                        ${reviews.length > 0 ? reviews.map(review => `
                            <div style="background: #f9fafb; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                    <strong>${review.username}</strong>
                                    <span style="color: #fbbf24;">⭐ ${review.rating}</span>
                                </div>
                                <p style="color: #666;">${review.review_text}</p>
                                <p style="color: #999; font-size: 0.85em; margin-top: 5px;">${review.review_date}</p>
                            </div>
                        `).join('') : '<p style="color: #999;">No reviews yet</p>'}
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <a href="https://www.google.com/maps?q=${restaurant.latitude},${restaurant.longitude}" 
                           target="_blank"
                           style="display: inline-block; background: #667eea; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
                            Get Directions
                        </a>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
        }
        
        // Load options when page loads
        loadFormOptions();
    </script>
</body>
</html>
'''


# ============================================================================
# 5. RUN THE APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("RESTAURANT RECOMMENDATION SYSTEM - FULL STACK")
    print("="*80)
    print("\nArchitecture:")
    print("  1. User fills preference form (Frontend)")
    print("  2. Preferences sent to Flask API (Backend)")
    print("  3. API calls ML Model → Returns place_ids")
    print("  4. API queries Database → Gets full details")
    print("  5. Complete data sent back to Frontend")
    print("\nEndpoints:")
    print("  GET  /                              - User preference form")
    print("  GET  /api/preferences/options       - Form dropdown options")
    print("  POST /api/recommendations           - Get personalized recommendations")
    print("  GET  /api/restaurant/<place_id>     - Full restaurant details")
    print("  GET  /api/similar/<place_id>        - Similar restaurants")
    print("  GET  /api/health                    - System health check")
    print("\nDatabase Tables:")
    print("  - restaurants          (351 records)")
    print("  - reviews             (3456 records)")
    print("  - user_preferences    (tracks user searches)")
    print("  - recommendation_logs (tracks recommendations)")
    print("\nOpen your browser:")
    print("  → http://localhost:5000")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)