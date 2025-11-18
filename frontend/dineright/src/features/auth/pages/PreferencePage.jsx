import React, { useState } from "react";
import "./PreferencePage.css";
import { prefapi } from "../authservice";
import { useSelector,useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { loginStart, loginSuccess, loginFailure } from "../authSlice";


const PreferencePage = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [selectedCuisines, setSelectedCuisines] = useState([]);
  const [selectedBudget, setSelectedBudget] = useState("");
  const [selectedAtmosphere, setSelectedAtmosphere] = useState("");
  const [selectedRestaurantType, setSelectedRestaurantType] = useState([]);
  const [address, setselectedAddress] = useState("");
  const [selectedAmenities, setSelectedAmenities] = useState([]);
  const [radius, setRadius] = useState(""); // 5 or 10 km
  const [showCuisineDropdown, setShowCuisineDropdown] = useState(false);
  const [showTypeDropdown, setShowTypeDropdown] = useState(false);
  const userid = useSelector((state) => state.auth.user?.id);
  console.log("UserID: ",userid);
  
  const convertList = (arr) => arr.map(item => ({ name: item }));

  const formData = {userId:userid,preferenceObject:{location:address,priceLevel:selectedBudget, cuisines:convertList(selectedCuisines),radius:radius, atmosphere:selectedAtmosphere,restaurantTypes:convertList(selectedRestaurantType),amenities:convertList(selectedAmenities)}}
 
  // --- Options ---
  const cuisines = [
    "Irish", "Sweet and Savory", "Continental", "Italian", "Japanese", "American",
    "Indian", "Mexican", "Middle Eastern", "Asian", "Portuguese", "French", "Mediterranean"
  ];

  const budgets = [
    { id: "b1", label: "€0 - €10",level:1 },
    { id: "b2", label: "€10 - €20",level:2 },
    { id: "b3", label: "€20 - €40",level:3 },
    { id: "b4", label: "€40+",level:4 },
  ];

  const atmosphereOptions = [
    { id: "a1", label: "Casual" },
    { id: "a2", label: "Lively" },
    { id: "a3", label: "Trendy" }
  ];

  const restaurantTypes = [
    "Cafe", "Pub", "Restaurant", "Bar", "Street Food", "Bistro", "Pizzeria", "Deli"
  ];

  const amenities = ["Bar", "Live music Bar"];

  // --- Handlers ---
  const toggleMultiSelect = (selectedArray, setArray, value) => {
    if (selectedArray.includes(value)) {
      setArray(selectedArray.filter((v) => v !== value));
    } else {
      setArray([...selectedArray, value]);
    }
  };

  const handleSubmit = async(e) => {
    e.preventDefault();
    try {
      const preferences = await prefapi(formData)
      console.log("Preferences:", formData);
      if (preferences.code=="SUCCESS"){
        console.log("Preference Saved");
        navigate(`/home/${userid}`)
      }
      else {
            dispatch(loginFailure("Signup failed"));
            alert("Saving Preference failed. Please try again.");
          }

    } catch (error) {
      dispatch(loginFailure(error.message));
      alert("Error connecting to server.");
    }
    // navigate to next page or save preferences
  };

  
  return (
    <div className="pref-container">
      <div className="pref-box">
        <h1 className="app-name">Dine Right</h1>
        <h2 className="pref-title">Choose Your Preferences</h2>

        <form onSubmit={handleSubmit} className="pref-form">
        <div className="section-row">
          <div className="section">
            <h3 className="section-title">Address</h3>
             <input type="text" name="address" placeholder="eg:Patrick Street, Cork" onChange={(e) => setselectedAddress(e.target.value)} value={address} />
          </div>
          <div>
              
          </div>
          <div className="section">
              <h3 className="section-title">Radius (km)</h3>
              <div className="options-grid">
                {[5, 10].map((r) => (
                  <div
                    key={r}
                    className={`option ${radius === r ? "selected" : ""}`}
                    onClick={() => setRadius(r)}
                  >
                    {r} km
                  </div>
                ))}
              </div>
            </div>
        </div>

          
          {/* --- Budget (single-select) --- */}
          
        <div className="section-row">

          <div className="section">
              <h3 className="section-title">Favourite Cuisines</h3>
              <div className="dropdown">
                <button
                  type="button"
                  className="dropdown-btn"
                  onClick={() => setShowCuisineDropdown(!showCuisineDropdown)}
                >
                  {selectedCuisines.length > 0
                    ? `${selectedCuisines.length} Selected`
                    : "Select cuisines"}
                </button>
                {showCuisineDropdown && (
                  <div className="dropdown-menu">
                    {cuisines.map((c) => (
                      <div
                        key={c}
                        className={`dropdown-item ${
                          selectedCuisines.includes(c) ? "selected" : ""
                        }`}
                        onClick={() =>
                          toggleMultiSelect(selectedCuisines, setSelectedCuisines, c)
                        }
                      >
                        {c}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {selectedCuisines.length > 0 && (
                <div className="selected-tags">
                  {selectedCuisines.map((c) => (
                    <span key={c} className="tag">
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          <div className="section">
            <h3 className="section-title">Budget Range</h3>
            <div className="options-grid">
              {budgets.map((b) => (
                <div
                  key={b.id}
                  className={`option ${selectedBudget === b.level ? "selected" : ""}`}
                  onClick={() => setSelectedBudget(b.level)}
                >
                  {b.label}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Row 2: Atmosphere + Restaurant Type */}
        <div className="section-row">
          {/* --- Atmosphere (single-select) --- */}
          <div className="section">
            <h3 className="section-title">Atmosphere</h3>
            <div className="options-grid">
              {atmosphereOptions.map((a) => (
                <div
                  key={a.id}
                  className={`option ${selectedAtmosphere === a.id ? "selected" : ""}`}
                  onClick={() => setSelectedAtmosphere(a.id)}
                >
                  {a.label}
                </div>
              ))}
            </div>
          </div>

          {/* --- Restaurant Type (multi-select) --- */}
          <div className="section">
              <h3 className="section-title">Restaurant Type</h3>
              <div className="dropdown">
                <button
                  type="button"
                  className="dropdown-btn"
                  onClick={() => setShowTypeDropdown(!showTypeDropdown)}
                >
                  {selectedRestaurantType.length > 0
                    ? `${selectedRestaurantType.length} Selected`
                    : "Select types"}
                </button>
                {showTypeDropdown && (
                  <div className="dropdown-menu">
                    {restaurantTypes.map((r) => (
                      <div
                        key={r}
                        className={`dropdown-item ${
                          selectedRestaurantType.includes(r) ? "selected" : ""
                        }`}
                        onClick={() =>
                          toggleMultiSelect(selectedRestaurantType, setSelectedRestaurantType, r)
                        }
                      >
                        {r}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {selectedRestaurantType.length > 0 && (
                <div className="selected-tags">
                  {selectedRestaurantType.map((r) => (
                    <span key={r} className="tag">
                      {r}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

        {/* Row 3: Dietary + Amenities */}
        <div className="section-row">
          {/* --- Dietary Options (multi-select) --- */}
    

          {/* --- Amenities (multi-select) --- */}
          <div className="section">
            <h3 className="section-title">Amenities</h3>
            <div className="options-grid">
              {amenities.map((a) => (
                <div
                  key={a}
                  className={`option ${selectedAmenities.includes(a) ? "selected" : ""}`}
                  onClick={() => toggleMultiSelect(selectedAmenities, setSelectedAmenities, a)}
                >
                  {a}
                </div>
              ))}
            </div>
          </div>
        </div>

        <button type="submit" className="submit-btn">
          Continue
        </button >
      </form>

      </div>
    </div>
  );
};

export default PreferencePage;
