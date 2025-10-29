// src/features/auth/pages/LoginPage.jsx
import React, { useState } from "react";
import { Link, useNavigate} from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { loginStart, loginSuccess, loginFailure } from "../authSlice";
import { loginUser } from "../authservice";


import "./LoginPage.css";

const LoginPage = () => {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state) => state.auth);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Login attempt:", formData);
    if (formData.password.length < 6) {
      alert("Password must be at least 6 characters long.");
      return;
    }
    try {
      dispatch(loginStart());
      const data = loginUser(formData.email, formData.password);


      if (data.code === "SUCCESS") {
        dispatch(loginSuccess({ id: data.id, email: formData.email }));
        navigate("/home", { replace: true });
      } else {
        dispatch(loginFailure("Invalid credentials"));
        alert("Invalid email or password");
      }
    } catch (err) {
      dispatch(loginFailure(err.message));
      alert("Login failed");
    }
    // later: dispatch(login(formData))
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="app-name">Dine Right</h1>
        
        <h2 className="text-2xl font-semibold text-center mb-6">Login</h2>

        <form onSubmit={handleSubmit} className="login-form">
          <div>
            <label className="emaillabel">Email</label>
            
            <input
              type="text"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label className="passwordlabel">Password</label>
            
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200"
              placeholder="Enter your password"
              required
            />
            
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700 transition"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="signup-text">
          Don’t have an account?{" "}
          <Link to="/signup" className="signup-link">
            Sign up
          </Link>
        </p>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>
    </div>
  );
};

export default LoginPage;
