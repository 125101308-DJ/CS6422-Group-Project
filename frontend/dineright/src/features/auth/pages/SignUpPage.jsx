// src/features/auth/pages/SignUpPage.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./SignUpPage.css";
import { useNavigate } from "react-router-dom";


const SignUpPage = () => {

  const navigate = useNavigate()
  const [formData, setFormData] = useState({ name: "", email: "", password: "" });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Sign up attempt:", formData);
    navigate("/preferences");
    // later: dispatch(signup(formData))
  };

  return (
    <div className="signup-container">
      <div className="signup-box">
        <h1 className="app-name">Dine Right</h1>
        <h2 className="text-2xl font-semibold text-center mb-6">Create Account</h2>

        <form onSubmit={handleSubmit} className="signup-form">
          <div>
            <label className="namelabel">Full Name</label>
            
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring focus:ring-blue-200"
              placeholder="Enter your name"
              required
            />
          </div>
            
          <div>
            <label className="emaillabel">Email</label>
            
            <input
              type="email"
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
              placeholder="Create a password"
              required
            />
          </div>

          {/* <Link to="/preferences"> */}
          <button
            type="submit"
            className="w-full bg-green-600 text-white rounded-lg py-2 hover:bg-green-700 transition">
            Sign Up
          </button>
          
          {/* </Link> */}
        </form>

        <p className="signuptext">
          Already have an account?{" "}
          <Link to="/login" className="signuplink">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default SignUpPage;
