import {React,useState,useEffect} from 'react'
import Sidebar from "../components/Sidebar";
import { useSelector } from 'react-redux';
import { getRestaurantVisitedById,getMockRestaurantVisitedById } from '../homeservice';
import "./RestaurantvisitedPage.css";
import { useNavigate } from 'react-router-dom';





const RestaurantvisitedPage = () => {
    const [visited, setVisited] = useState([]);
    const navigate = useNavigate()
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const handleSidebarToggle = (open) => {
        setIsSidebarOpen(open);};
    console.log(isSidebarOpen);
    
    const userId = useSelector((state) => state.auth.user?.id);
    useEffect(() => {
      const loadVisitedRestaurants  = async () => {
        try {
          const data = await getMockRestaurantVisitedById(userId)
          console.log("Data: ",data);
          console.log("Rest Data: ",data.restaurantsVisited);
          
          if (data.code === "SUCCESS") {
          setVisited(data.restaurantsVisited || []);
          console.log(visited);
          
        } else {
          setError("Failed to fetch visited restaurants.");
        }
        } catch (error) {
            console.error("Error fetching Restaurants Visited:", error);
            alert("Error loading restaurant data.");
        }
      }
      loadVisitedRestaurants()
    
      
    }, [userId])
    const handleRestaurantClick = (restaurant) => {
    navigate(`/restaurant/${restaurant.restaurantId}`);
};
      
  return (
    <div className="restaurantvisited-container">
      <Sidebar onToggle={handleSidebarToggle} />
      <main className={`restaurantvisited-main ${isSidebarOpen ? "open" : "collapsed"}`}>
        <h1>Restaurants You Visited</h1>

        <div className="visited-grid">
          {
            visited.map((restaurant) => (
              <div
                key={restaurant.restaurantId}
                className="visited-card"
                onClick={() => handleRestaurantClick(restaurant)}
              >
                <img
                  src="/assets/restaurantimg.jpg"
                  alt={restaurant.restaurantName}
                  className="visited-img"
                />
                <div className="visited-info">
                  <h3>{restaurant.restaurantName}</h3>
                  <p>{restaurant.Location}</p>
                </div>
              </div>
            )
          )}
        </div>
      </main>
    </div>
  );
}

export default RestaurantvisitedPage