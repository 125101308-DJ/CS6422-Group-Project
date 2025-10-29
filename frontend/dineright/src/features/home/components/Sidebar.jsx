import React from "react";
import "./Sidebar.css";
import { logout } from "../../auth/authSlice";
import { useDispatch } from "react-redux";
import { useNavigate, NavLink } from "react-router-dom";

const Sidebar = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login", { replace: true });
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">🍽️ Dine Right</div>

      <nav className="sidebar-menu">
        <NavLink
          to="/home"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          Overview
        </NavLink>

        <NavLink
          to="/mycorner"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          My Corner
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          Settings
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        {/* <img
          src="https://i.pravatar.cc/40"
          alt="User Avatar"
          className="sidebar-avatar"
        /> */}
        <div>
          <p className="sidebar-name">John Doe</p>
          <p className="sidebar-email">john@example.com</p>
        </div>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>
    </aside>
  );
};

export default Sidebar;