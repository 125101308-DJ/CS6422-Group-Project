# Dine Right

**Smart Restaurant Recommendations for Ireland**

> *Discover your next favorite dining spot with intelligent, personalized recommendations powered by real user experiences and advanced machine learning.*

---

## Table of Contents

- [About the Project](#about-the-project)
- [Why Dine Right?](#why-dine-right)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Team](#team)


---

## About the Project

**Dine Right** is an intelligent web-based restaurant recommendation system designed specifically for food lovers in Cork, Ireland. Whether you're a local looking for a new dining experience or a visitor exploring Irish's culinary scene, Dine Right helps you find the perfect restaurant that matches your unique preferences.

Built as part of the **CS6422 Group Project** by **Group Ingenious**, this platform combines the power of collaborative and content-based filtering to deliver personalized dining recommendations that truly understand what you're looking for.

---

## Why Dine Right?

### The Problem
Finding the right restaurant can be overwhelming. Generic review platforms show you everything but rarely understand *your* preferences. You might be craving Italian food in a cozy setting near your location, but most platforms make you sift through hundreds of irrelevant options.

### Our Solution
Dine Right learns your preferences during signup and continuously improves recommendations based on your reviews and dining history. By analyzing both your tastes and patterns from similar users, we surface restaurants you'll genuinely love — not just the most popular ones.

### What Makes Us Different
- **Hyper-local focus**: Exclusively curated for Cork, Ireland
- **Preference-driven**: Built around *your* dining style, not generic ratings
- **Community-powered**: Real reviews from real diners shape recommendations
- **Conversational AI**: Get instant help finding your perfect meal through our chatbot

---

## Key Features

### Cuisine-Based Discovery
Browse restaurants by your favorite cuisines — Italian, Indian, Chinese, Mexican, Irish, and more. Our system understands nuanced preferences like "authentic Thai" vs. "fusion Asian."

### Location-Aware Recommendations
Whether you're in the city center, near UCC, or exploring the suburbs, Dine Right suggests restaurants within your preferred distance. No more finding the perfect restaurant only to realize it's 30km away.

### Ambience Matching
Looking for a romantic dinner spot? A family-friendly café? A trendy bar? We factor in the atmosphere so you get the right vibe, not just the right food.

### Review-Driven Intelligence
Our recommendation engine doesn't just count stars — it analyzes review sentiment, identifies what people truly enjoyed, and surfaces restaurants with qualities you care about.

### User Reviews & Ratings
After dining, share your experience to help others discover great spots. Your feedback directly improves recommendations for users with similar tastes.

### AI-Powered Chatbot
Stuck deciding where to eat? Chat with our intelligent assistant to get instant recommendations, ask about specific cuisines, check opening hours, or even get directions — all in natural conversation.

---

## How It Works

### Recommendation Engine

Dine Right employs a **hybrid recommendation system** that combines multiple approaches for superior accuracy:

#### 1️⃣ **Content-Based Filtering**
Matches restaurant attributes (cuisine type, price range, ambience, location, dietary options) with your stated preferences. If you love Italian food and cozy settings, we'll prioritize restaurants that fit this profile.

#### 2️⃣ **Collaborative Filtering**
Analyzes patterns from users with similar tastes. If users who love the same restaurants as you also rave about a new café, we'll recommend it to you — even if it's outside your usual preferences.

#### 3️⃣ **Hybrid Approach**
Combines both methods to overcome the limitations of each. This ensures great recommendations for new users (cold start problem) while leveraging community wisdom for personalized suggestions.

### Data Pipeline

```
User Preferences → Feature Engineering → ML Model → Personalized Rankings → User Feedback → Model Refinement
```

1. **Data Collection**: Web scraping from Google Maps to gather restaurant info and reviews
2. **Feature Engineering**: Extract meaningful attributes (cuisine types, sentiment scores, location data)
3. **Model Training**: Train collaborative and content-based models on historical user data
4. **Real-time Recommendations**: Generate personalized suggestions based on current user context
5. **Continuous Learning**: Update models as users add reviews and ratings

---

## Technology Stack

### Frontend
- **React.js** - Modern, responsive user interface
- **Tailwind CSS** - Clean, utility-first styling
- **Axios** - API communication
- **React Router** - Seamless navigation

### Backend
- **Python / Flask** - RESTful API server
- **FastAPI** - High-performance endpoints (alternative)
- **PostgreSQL** - Relational database for structured data
- **Redis** - Caching layer for fast recommendations

### Machine Learning
- **scikit-learn** - Collaborative filtering algorithms
- **Pandas & NumPy** - Data manipulation and feature engineering
- **NLTK / spaCy** - Natural language processing for review analysis
- **TensorFlow / PyTorch** - Deep learning models (optional advanced features)

### Data Collection
- **Selenium** - Web scraping for restaurant data
- **BeautifulSoup** - HTML parsing
- **Google Maps API** - Location and review data

### Deployment
- **Docker** - Containerization
- **AWS / Heroku** - Cloud hosting
- **GitHub Actions** - CI/CD pipeline

---

## Project Structure

 In-Progress
---

## Team

**Group Ingenious** - CS6422 Group Project

| Role | Name | Responsibilities |
|------|------|-----------------|
| **Backend Developer** | Derick | API development, database design, authentication |
| **Frontend Developer** | Ashfaq | UI/UX design, React components, user interface |
| **AI Engineer** | Vishvasundar | Data collection, ML model development, recommendation engine |
| **Data Engineer/Tester** | Deepak | Data Collection, Schema Design, Integration, Deployment, Testing, Containerization |
| **Product Owner / ML Engineer** | Harini Sri | Coordination, documentation, timeline management, Building Chatbot|

---
