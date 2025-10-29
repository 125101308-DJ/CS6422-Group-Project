import {React,useState, useEffect} from "react";
import Sidebar from "../components/Sidebar";
import "./HomePage.css";
import { useNavigate } from "react-router-dom";




const fetchRestaurants = async () => {
  // simulate backend delay
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 1,
          name: "Blue Ocean Seafood",
          location: "Miami",
          cuisine: "Seafood",
          reviews: [
            { user: "John", rating: 4.8, comment: "Amazing food!" },
          ],
        },
        {
          id: 2,
          name: "Spice Route",
          location: "New York",
          cuisine: "Indian",
          reviews: [
            { user: "Anna", rating: 4.6, comment: "Loved the spices!" },
          ],
        },
        {
          id: 3,
          name: "Tokyo Sushi House",
          location: "San Francisco",
          cuisine: "Japanese",
          reviews: [
            { user: "Mark", rating: 4.9, comment: "Best sushi in town!" },
          ],
        },
      ]);
    }, 1000);
  });
};


const HomePage = () => {
    const [restaurants, setRestaurants] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
    const loadRestaurants = async () => {
      const data = await fetchRestaurants();
      console.log("loading rest data");
      
      setRestaurants(data);
      setFiltered(data); // initially show all
    };
    loadRestaurants();
  }, []);


    const handleSearch = (e) => {
    const value = e.target.value.toLowerCase();
    setSearchTerm(value);

    const filteredResults = restaurants.filter(
      (r) =>
        r.name.toLowerCase().includes(value) ||
        r.location.toLowerCase().includes(value) ||
        r.cuisine.toLowerCase().includes(value)
    );
    setFiltered(filteredResults);
  };

    const handleRestaurantClick = (id) => {
    // redirect to restaurant detail page (we’ll create later)
    navigate(`/restaurant/${id}`);
  };






  return (
    <div className="home-container">
      <Sidebar />

      <main className="home-content">
        <header className="home-header">
          <div className="header-top">
            <h1>Welcome back, John!</h1>
            <div className="search-wrapper">
              <input
                type="text"
                className="search-bar"
                placeholder="Search restaurants..."
                value={searchTerm}
                onChange={handleSearch}
              />

              {/* 🔍 Show search results dropdown only if user typed something */}
              {searchTerm && (
                <div className="search-results">
                  {filtered.length > 0 ? (
                    filtered.map((restaurant) => (
                      <div
                        key={restaurant.id}
                        className="search-result-item"
                        onClick={() => handleRestaurantClick(restaurant.id)}
                      >
                        <strong>{restaurant.name}</strong>
                        <p>{restaurant.cuisine} · {restaurant.location}</p>
                      </div>
                    ))
                  ) : (
                    <p className="no-results">No restaurants found.</p>
                  )}
                </div>
              )}
            </div>
          </div>
          <p>Here’s what’s happening with your dining journey today.</p>
        </header>

        <section className="stats-section">
          <div className="stat-card">
            <h3>Restaurants Visited</h3>
            <p className="stat-number">47</p>
          </div>

          <div className="stat-card">
            <h3>Reviews Written</h3>
            <p className="stat-number">31</p>
          </div>
          <div className="stat-card">
            <h3>Wishlist</h3>
            <p className="stat-number">31</p>
          </div>
        </section>

        <section className="recommend-section">
          <h2>Recommended for You</h2>
          <p className="recommend-subtitle">
            Based on your preferences and dining history
          </p>

          <div className="recommend-list">
            <div className="recommend-card">
              <div className="recommend-text">
                <h4>Restaurant 1</h4>
                <p className="recommend-details">Seafood · 4.8 ★ · 0.8 miles</p>
              </div>
              <span className="recommend-match">95% match</span>
            </div>

            <div className="recommend-card">
              <div className="recommend-text">
                <h4>Restaurant 2</h4>
                <p className="recommend-details">Indian · 4.6 ★ · 1.2 miles</p>
              </div>
              <span className="recommend-match">89% match</span>
            </div>
          </div>
        </section>
        {/* <section className="recommend-section" style={{ marginTop: "24px" }}>
          <h2>Restaurants</h2>
          <p className="recommend-subtitle">Browse and discover your next favorite spot</p>

          <div className="recommend-list">
            {filtered.length === 0 ? (
              <p>No restaurants found.</p>
            ) : (
              filtered.map((restaurant) => (
                <div
                  key={restaurant.id}
                  className="recommend-card"
                  onClick={() => handleRestaurantClick(restaurant.id)}
                >
                  <div className="recommend-text">
                    <h4>{restaurant.name}</h4>
                    <p className="recommend-details">
                      {restaurant.cuisine} · {restaurant.location} · {restaurant.rating} ★
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </section> */}
      </main>
    </div>
  );
};

export default HomePage;
