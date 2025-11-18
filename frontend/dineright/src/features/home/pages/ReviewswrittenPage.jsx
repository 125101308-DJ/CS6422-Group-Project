import { React, useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import "./ReviewswrittenPage.css";
import { getReviewsWrittenById,getMockReviewsWrittenById } from "../homeservice";

const ReviewsWrittenPage = () => {
  const [reviews, setReviews] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const userId = useSelector((state) => state.auth.user?.id);
  const navigate = useNavigate();

  const handleSidebarToggle = (open) => {
    setIsSidebarOpen(open);
  };

  useEffect(() => {
    const loadReviews = async () => {
      try {
        // const data = await getReviewsWrittenById(userId);
        const data = await getMockReviewsWrittenById(userId);

        if (data.code === "Success") {
          setReviews(data.reviewsWritten || []);
        } else {
          alert("Failed to fetch reviews.");
        }
      } catch (error) {
        console.error("Error fetching reviews:", error);
        alert("Error loading review data.");
      }
    };

    loadReviews();
  }, [userId]);

  const handleRestaurantClick = (restaurantId) => {
    navigate(`/restaurant/${restaurantId}`);
  };

  return (
    <div className="reviews-container">
      <Sidebar onToggle={handleSidebarToggle} />

      <main
        className={`reviews-main ${
          isSidebarOpen ? "open" : "collapsed"
        }`}
      >
        <h1>Reviews You Have Written</h1>

        <div className="reviews-grid">
          {reviews.map((review) => (
            <div
              key={review.restaurantId}
              className="reviews-card"
              onClick={() => handleRestaurantClick(review.restaurantId)}
            >
              <img
                src="/assets/restaurantimg.jpg"
                alt={review.restaurantName}
                className="reviews-img"
              />

              <div className="reviews-info">
                <h3>{review.restaurantName}</h3>
                <p className="review-text">{review.reviewWritten}</p>
              </div>
            </div>
          ))}
        </div>

        {reviews.length === 0 && (
          <p className="no-data">You haven't written any reviews yet.</p>
        )}
      </main>
    </div>
  );
};

export default ReviewsWrittenPage;
