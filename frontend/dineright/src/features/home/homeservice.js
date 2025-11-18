import axios from "axios";
import { API_BASE_URL } from "../../config";



export async function fetchrestaurantsapi() {
    try {
        const response = await axios.get(`${API_BASE_URL}/getAllRestaurantsData`)
        return response.data
        
    } catch (error) {
        console.error("Login API error:", error);
        return  {code: "FAIL", message: error.message }
    }
}


export async function addreviewapi(reviewdata) {
    try {
        const res = await axios.post(`${API_BASE_URL}/add`, reviewdata)
        return res.data
        
    } catch (error) {
        console.error("Review Add API error:", error);
        return  {code: "FAIL", message: error.message }
        
    }
    
}


export async function getRestaurantById(params) {
    try {
        const response = axios.get(`${API_BASE_URL}/getRestaurantsDataById/${params}`)
        return response.data
    } catch (error) {
        console.error("Restaurant By ID API Failed:", error);
        return  {code: "FAIL", message: error.message }
        
    }
}


export async function getRestaurantVisitedById(params) {
    try {
        const response = axios.getget(`${API_BASE_URL}/getRestaurantsVisitedId/${params}`)
        return response.data
    } catch (error) {
        console.error("Restaurant Visited By ID API Failed:", error);
        return  {code: "FAIL", message: error.message }
        
    }
}
export async function getReviewsWrittenById(userId) {
  try {
    const response = await axios.get(`${API_BASE_URL}/getReviewsWritten/${userId}`);
    return response.data;
  } catch (error) {
    console.error("Reviews Written API Failed:", error);
    return { code: "FAIL", message: error.message };
  }
}
export async function getMockReviewsWrittenById(userId) {
  try {
        const response = {code:"Success",reviewsWritten :[{restaurantId:1,restaurantName: "Salt n pepper",reviewWritten :"Very Nice Very Good" },
            {restaurantId:2,restaurantName: "Salt or pepper",Location:"Cork",reviewWritten :"Very Nice Very Good" },
             {restaurantId:3,restaurantName: "Muniyandi Vlias",Location:"Cork",reviewWritten :"Very Nice Very Good" }
        ]}
        return response
    } catch (error) {
        console.error("Restaurant Visited By ID API Failed:", error);
        return  {code: "FAIL", message: error.message }
        
    }
}
export async function getMockRestaurantVisitedById(params) {
    try {
        const response = {code:"SUCCESS",restaurantsVisited:[{restaurantId:1,restaurantName: "Salt n pepper",Location:"Cork" },
            {restaurantId:2,restaurantName: "Salt or pepper",Location:"Cork" },
             {restaurantId:3,restaurantName: "Muniyandi Vlias",Location:"Cork" }
        ]}
        return response
    } catch (error) {
        console.error("Restaurant Visited By ID API Failed:", error);
        return  {code: "FAIL", message: error.message }
        
    }
}




export async function addToWishListApi(userId, restaurantId) {
    try {
        const res = await axios.post(`${API_BASE_URL}/addWishlist`, {
      userId,
      restaurantId,
    });
    return res.data;
    
    } catch (error) {
        return { code: "FAIL", message: error.message };
    }
}


export async function removeFromWishlist(userId, restaurantId) {
  try {
    const res = await axios.delete(`${API_BASE_URL}/removeWishlist`,{ userId, restaurantId } );
    return res.data;
  } catch (error) {
    return { code: "FAIL", message: error.message };
  }
}


export async function addToVisited(userId, restaurantId) {
  try {
    const res = await axios.post(`${API_BASE_URL}/addVisited`, {
      userId,
      restaurantId,
    });
    return res.data;
  } catch (error) {
    return { code: "FAIL", message: error.message };
  }
}

// REMOVE visited
export async function removeFromVisited(userId, restaurantId) {
  try {
    const res = await axios.delete(`${API_BASE_URL}/removeVisited`, { userId, restaurantId });
    return res.data;
  } catch (error) {
    return { code: "FAIL", message: error.message };
  }
}