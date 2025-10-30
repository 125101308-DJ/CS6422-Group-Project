import axios from "axios";
import { API_BASE_URL } from "../../config";



export async function fetchrestaurantsapi() {
    try {
        const response = await axios.get(`${API_BASE_URL}/login`)
        return response.data
        
    } catch (error) {
        console.error("Login API error:", error);
        return  {code: "FAIL", message: error.message }
    }
}