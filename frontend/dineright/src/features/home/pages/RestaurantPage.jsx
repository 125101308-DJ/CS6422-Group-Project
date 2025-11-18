import React from 'react'
import {useState, useEffect} from 'react'
import { useParams, useLocation } from 'react-router-dom'
import "./RestaurantPage.css"
import { useSelector } from 'react-redux'
import { addreviewapi,getRestaurantById, addToVisited, addToWishListApi,removeFromWishlist,removeFromVisited } from '../homeservice'

// useLocation() is a React Router hook that gives you access to the current route’s information, including:

// the current pathname (like /restaurant/2)

// any search params (?query=sushi)

// and most importantly — any state that was passed via navigate()


const RestaurantPage = () => {
    const { id } = useParams();
    const uselocation = useLocation();
    const userId = useSelector((state) => state.auth.user?.id);
    const [restaurant, setRestaurant] = useState(uselocation.state?.restaurant || null);    const [showModal, setShowModal] = useState(false);
    const [userrating, setRating] = useState("");
    const [comment, setComment] = useState("");
    const [loading, setLoading] = useState(false);
    const [isWishlisted, setIsWishlisted] = useState(false);
    const [isVisited, setIsVisited] = useState(false);
    if (!restaurant) {
    return <div>No restaurant data available. Please go back to home.</div>;
  }
    const loadrestaurantbyid = async()=> {
      try {
        const data = await getRestaurantById(id)
        const list = data.restaurantData || data.restaurants || [];
        if (data.code === "SUCCESS" && Array.isArray(list)) {
          setRestaurant(list);
          
        } else {
          console.error("Failed to load restaurants by ID API:", data);
          alert("Could not load restaurants. Please try again later.");
        } 
      } catch (error) {
        console.error("Error fetching restaurants:", error );
        alert("Error loading restaurant data.");
        
      }
    }
     useEffect(() => {
       loadrestaurantbyid()
       console.log("Loading restaurant Data");
       
     }, [])
     
    const {name, location,price_range,atmosphere,amenities ,phoneNumber, rating, cuisine, reviews =[]} = restaurant
    const handleSaveReview = async () => {
    if (!rating) {
      alert("Please select a rating before saving.");
      return;
    }

    const reviewData = {
      userId,
      restaurantId: id,
      userrating,
      comment,
    };

    try {
      setLoading(true);
      const res = addreviewapi();
      console.log("Review saved:", res);
      setShowModal(false);
      setRating("");
      setComment("");
      await loadrestaurantbyid()
      // Optional: Refresh reviews list or show a success message
    } catch (error) {
      console.error("Error saving review:", error);
      alert("Failed to save review");
    } finally {
      setLoading(false);
    }
  };

    const handleWishlistToggle = async () => {
  if (!isWishlisted) {
    // ADD
    const res = await addToWishListApi(userId, id);
    if (res.code === "SUCCESS") {
      setIsWishlisted(true);
      alert("Added to wishlist!");
    }
  } else {
    // REMOVE
    const res = await removeFromWishlist(userId, id);
    if (res.code === "SUCCESS") {
      setIsWishlisted(false);
      alert("Removed from wishlist!");
    }
  }
};
    const handleVisitedToggle = async () => {
  if (!isVisited) {
    const res = await addToVisited(userId, id);
    if (res.code === "SUCCESS") {
      setIsVisited(true);
      alert("Marked as visited!");
    }
  } else {
    const res = await removeFromVisited(userId, id);
    if (res.code === "SUCCESS") {
      setIsVisited(false);
      alert("Removed from visited list!");
    }
  }
};
  return (
    <div className="restaurant-container">
      
      <main className="restaurant-content">
        <div className="restaurant-header">
          <img
            src="/assets/restaurantimg.jpg"
            alt={name}
            className="restaurant-image"
          />
          <div className="restaurant-info">
            <h1>{name}</h1>
            <div className="toggle-buttons">
              <button
                className={`wish-btn ${isWishlisted ? "active" : ""}`}
                onClick={handleWishlistToggle}
              >
                {isWishlisted ? "❤️ Wishlisted" : "🤍 Add to Wishlist"}
              </button>

              <button
                className={`visited-btn ${isVisited ? "active" : ""}`}
                onClick={handleVisitedToggle}
              >
                {isVisited ? "✔️ Visited" : "➕ Mark as Visited"}
              </button>
            </div>
            <p className="restaurant-meta">{cuisine} · {location} · {price_range} · {atmosphere} · {amenities} · {phoneNumber} </p>
            <p className="restaurant-rating">
              {/* ⭐{rating} */}
              ⭐4.5
            </p>
          </div>
          <div className="addreview">
            <button
              className="addreviewbtn"
              onClick={() => setShowModal(true)}
            >
              + Add Review
            </button>
          </div>
        </div>


        <section className="reviews-section">
          <h2>Customer Reviews</h2>
          {reviews.length === 0 ? (
            <p>No reviews yet.</p>
          ) : (
            <div className="reviews-list">
              {reviews.map((r, i) => (
                <div key={i} className="review-card">
                  <p className="review-user">{r.user}</p>
                  <p className="review-rating">⭐ {r.rating}</p>
                  <p className="review-comment">{r.comment}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Add Your Review</h3>

            <label>Rating (required):</label>
            <div className="rating-stars">
              {[1, 2, 3, 4, 5].map((num) => (
                <span
                  key={num}
                  className={`star ${userrating >= num ? "selected" : ""}`}
                  onClick={() => setRating(num)}
                >
                  ⭐
                </span>
              ))}
            </div>

            <label>Comment (optional):</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Write your thoughts..."
            />

            <div className="modal-buttons">
              <button onClick={() => setShowModal(false)} className="cancel-btn">
                Cancel
              </button>
              <button onClick={handleSaveReview} className="save-btn" disabled={loading}>
                {loading ? "Saving..." : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RestaurantPage