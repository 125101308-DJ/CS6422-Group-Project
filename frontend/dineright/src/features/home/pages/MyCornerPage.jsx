import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import "./MyCornerPage.css";


const MyCornerPage = () => {
  const [recentActivity] = useState([
    { id: 1, text: "You reviewed 'Spice Route' ★★★★☆" },
    { id: 2, text: "Added 'Tokyo Sushi House' to your Wishlist" },
    { id: 3, text: "Visited 'Blue Ocean Seafood'" },
  ]);

  const [wishlist] = useState([
    { id: 1, name: "Golden Curry", location: "Chicago" },
    { id: 2, name: "The Green Fork", location: "Austin" },
  ]);

  const [rankings] = useState([
    "Tokyo Sushi House",
    "Spice Route",
    "Blue Ocean Seafood",
    "Golden Curry",
    "The Green Fork",
    "Bella Italia",
    "Grill Master",
    "Ocean Breeze",
    "Taco Fiesta",
    "The Garden Plate",
  ]);

  return (
    <div className="mycorner-container">
      <Sidebar />

      <main className="mycorner-content">
        <header className="mycorner-header">
          <h1>My Corner</h1>
          <p>Your personal dining dashboard — all in one place.</p>
        </header>

        {/* Recent Activity Section */}
        <section className="activity-section">
          <h2>Recent Activity</h2>
          <ul className="activity-list">
            {recentActivity.map((item) => (
              <li key={item.id} className="activity-item">
                {item.text}
              </li>
            ))}
          </ul>
        </section>

        {/* Wishlist Section */}
        <section className="wishlist-section">
          <h2>My Wishlist</h2>
          <div className="wishlist-grid">
            {wishlist.map((r) => (
              <div key={r.id} className="wishlist-card">
                <h4>{r.name}</h4>
                <p>{r.location}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Top 10 Rankings Section */}
        <section className="ranking-section">
          <h2>Top 10 Restaurants</h2>
          <p className="ranking-subtitle">Your current personal favorites</p>
          <ul className="ranking-list">
            {rankings.map((name, index) => (
              <li key={index} className="ranking-item">
                <span className="rank-number">{index + 1}</span>
                <span className="rank-name">{name}</span>
                {/* We’ll add reorder buttons later here */}
              </li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  );
};

export default MyCornerPage;
