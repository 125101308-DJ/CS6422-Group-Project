import React, { useState } from "react";
import "./PreferencePage.css";

const PreferencePage = () => {
  const [selectedCuisines, setSelectedCuisines] = useState([]);
  const [selectedBudget, setSelectedBudget] = useState("");

  const cuisines = [
    "Italian",
    "Chinese",
    "Indian",
    "Mexican",
    "Japanese",
    "French",
    "Irish"
  ];

  const budgets = [
    { id: "b1", label: "€0 - €10" },
    { id: "b2", label: "€10 - €20" },
    { id: "b3", label: "€20 - €40" },
    { id: "b4", label: "€40+" },
  ];

  const handleCuisineSelect = (cuisine) => {
    if (selectedCuisines.includes(cuisine)) {
      setSelectedCuisines(selectedCuisines.filter((c) => c !== cuisine));
    } else {
      setSelectedCuisines([...selectedCuisines, cuisine]);
    }
  };

  const handleBudgetSelect = (budgetId) => {
    setSelectedBudget(budgetId);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Preferences:", { selectedCuisines, selectedBudget });
    // navigate('/home') or next page logic here
  };

  return (
    <div className="pref-container">
      <div className="pref-box">
        <h1 className="app-name">Dine Right</h1>
        <h2 className="pref-title">Choose Your Preferences</h2>

        <form onSubmit={handleSubmit} className="pref-form">
          {/* Cuisine selection */}
          <div className="section">
            <h3 className="section-title">Favourite Cuisines</h3>
            <div className="options-grid">
              {cuisines.map((cuisine) => (
                <div
                  key={cuisine}
                  className={`option ${
                    selectedCuisines.includes(cuisine) ? "selected" : ""
                  }`}
                  onClick={() => handleCuisineSelect(cuisine)}
                >
                  {cuisine}
                </div>
              ))}
            </div>
          </div>

          {/* Budget selection */}
          <div className="section">
            <h3 className="section-title">Budget Range</h3>
            <div className="options-grid">
              {budgets.map((budget) => (
                <div
                  key={budget.id}
                  className={`option ${
                    selectedBudget === budget.id ? "selected" : ""
                  }`}
                  onClick={() => handleBudgetSelect(budget.id)}
                >
                  {budget.label}
                </div>
              ))}
            </div>
          </div>

          <button type="submit" className="submit-btn">
            Continue
          </button>
        </form>
      </div>
    </div>
  );
};

export default PreferencePage;
