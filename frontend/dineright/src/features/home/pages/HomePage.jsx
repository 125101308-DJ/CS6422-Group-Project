import {React,useState, useEffect} from "react";
import Sidebar from "../components/Sidebar";
import "./HomePage.css";
import { useNavigate, useParams, NavLink } from "react-router-dom";
import { fetchrestaurantsapi,getRecommendationApi } from "../homeservice";
import Chatbot from "../components/chatbot";


const fetchRestaurants = async () => {
  // simulate backend delay
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(
        {
          code:"SUCCESS",
          restaurants:[
            { id: 1, name: "Blue Ocean Seafood", location: "Miami",price_range:"10-20",atmosphere:"Lively",amenities:"Live Music" ,phoneNumber:"326655624", rating: 4.5, cuisine: "Seafood", reviews: [ { user: "John", rating: 4.8, comment: "Amazing food!" }, ], }, { id: 2, name: "Spice Route", location: "New York",rating: 4, cuisine: "Indian", reviews: [ { user: "Anna", rating: 4.6, comment: "Loved the spices!" }, ], }, { id: 3, name: "Tokyo Sushi House", location: "San Francisco",rating: 4.7, cuisine: "Japanese", reviews: [ { user: "Mark", rating: 4.9, comment: "Best sushi in town!" }, ], }
          ]
        }
      );
    }, 1000);
  });
};




const HomePage = () => {
    const [restaurants, setRestaurants] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [recommendedRestaurants, setRecommendedRestaurants] = useState(null)
    const { id } = useParams();
    const navigate = useNavigate();
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const handleSidebarToggle = (open) => {
    setIsSidebarOpen(open);
  };
    const result = {code:"Success", recommendedRestaurant:[{placeId:2,resname:"Karthi",location:"New York",
      cuisines:"Italian"}, {placeId:3,resname:"Ash",location:"Ireland",
      cuisines:"Indian"
    }] }
    
    
      
    
    // console.log("Recommendation:",res2[0])
    
    useEffect(() => {
    const loadRestaurants = async () => {
      // 
      try {
        const data = await fetchrestaurantsapi();
        // const data = await fetchRestaurants();
        
        
        console.log("Restaurants API Response:", data);
        const list = data.restaurantData || data.restaurants || [];
        if (data.code === "SUCCESS" && Array.isArray(list)) {
          setRestaurants(list);
          setFiltered(list);
        } else {
          console.error("Failed to load restaurants:", data);
          alert("Could not load restaurants. Please try again later.");
        }
      } catch (error) {
        console.error("Error fetching restaurants:", err);
        alert("Error loading restaurant data.");
      } // initially show all
    };
    loadRestaurants();
  }, []);

    useEffect(() => {
      const getrecomenndation = async () => {
        const data = await getRecommendationApi(id)
        console.log("Restaurant Recomendation API data: ",data);
        if (data.code=="Success" || Array.isArray(data.recommendedRestaurants ) ) {
          setRecommendedRestaurants(data.recommendedRestaurants)
        }
        
      }
    }, [])
    
    const handleSearch = (e) => {
    const value = e.target.value.toLowerCase();
    setSearchTerm(value);

    const filteredResults = restaurants.filter(
      (r) =>
        r.name.toLowerCase().includes(value) ||
        r.address.toLowerCase().includes(value) ||
        r.cuisine.toLowerCase().includes(value)
    );
    setFiltered(filteredResults);
  };

    const handleRestaurantClick = (restaurant) => {
    // redirect to restaurant detail page (we’ll create later)
    navigate(`/restaurant/${restaurant.placeId}`, {state:{restaurant}});
  };






  return (
    <div className="home-container">
      <Sidebar onToggle={handleSidebarToggle} />

      <main className={`home-content ${isSidebarOpen ? "shifted" : "full"}`}>
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
                        key={restaurant.placeId}
                        className="search-result-item"
                        onClick={() => handleRestaurantClick(restaurant)}
                      >
                        <strong>{restaurant.name}</strong>
                        <p>{restaurant.cuisine} · {restaurant.address}</p>
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
          <div className="stat-card" >
            <NavLink className={"navlink"}
              to={"/restaurantvisitedpage"}>
              <h3>Reviews Visited</h3>
              <p className="stat-number">47</p>
            </NavLink>

            
          </div>

          <div className="stat-card">
            <NavLink className={"navlink"}
              to={"/restaurantwrittenpage"}>
              <h3>Reviews Written</h3>
              <p className="stat-number">31</p>
            </NavLink>
            
          </div>
          <div className="stat-card">
            <NavLink className={"navlink"}
              to={"/mycorner"}>
              <h3>Wishlist</h3>
              <p className="stat-number">31</p>
            </NavLink>
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
              {/* <div >
                  {recommendedRestaurants.map((b)=>(
                  <><h4>{b.resname}</h4><p className="recommend-details">{b.cuisine} · {b.rating} ★ · {b.location}</p></>

                ))}
              </div>
             */}
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
      <Chatbot />
    </div>
  );
};

export default HomePage;
