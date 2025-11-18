import axios from "axios";
import { API_BASE_URL } from "../../config";




export function loginUser(email, password) {
  if (email === "test@gmail.com" && password === "123456") {
    return { code: "SUCCESS", id: 1 };
  } else {
    return { code: "FAIL" };
  }
}



export async function loginUserapi(email, password) {
  try {
    const response = await axios.post(`${API_BASE_URL}/login`, {email, password});
    return response.data
  } catch (error) {
    console.error("Login API error:", error);
    return  {code: "FAIL", message: error.message }
  }
}


export async function signupapi(name,email, password) {
  try {
    const response = await axios.post(`${API_BASE_URL}/signup`, {
      name, email, password
    })
    return response.data
    
  } catch (error) {
    console.error("Signup API error:", error);
    return  {code: "FAIL", message: error.message }
    
  }
}
export function signuser(name,email, password) {
  return { code: "SUCCESS", id: 1 };
}



export async function prefapi(formdata) {
  try {
    const response = await axios.post(`${API_BASE_URL}/savePrefs`, formdata)
    return response.data
    
  } catch (error) {
    console.error("Preference API error:", error);
    return  {code: "FAIL", message: error.message }
    
  }
}