import React from 'react'
import LoginPage from './features/auth/pages/LoginPage.jsx'
import SignUpPage from 'frontend/dineright/src/features/auth/pages/SignUpPage.jsx'
import PreferencePage from './features/auth/pages/PreferencePage.jsx';
import { Routes, Route } from "react-router-dom";
import ProtectedRoute from "./features/auth/components/routing/ProtectedRoute.jsx";
import HomePage from './features/home/pages/HomePage.jsx';
import MyCornerPage from './features/home/pages/MyCornerPage.jsx';
import RestaurantPage from './features/home/pages/RestaurantPage.jsx';
import RestaurantvisitedPage from './features/home/pages/RestaurantvisitedPage.jsx';
import ReviewswrittenPage from './features/home/pages/ReviewswrittenPage.jsx';


const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/preferences" element={<PreferencePage />} />
      <Route
        path="/home/:id"
        element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/mycorner"
        element={
          <ProtectedRoute>
            <MyCornerPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/restaurant/:id"
        element={
          <ProtectedRoute>
            <RestaurantPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/restaurantvisitedpage"
        element={
          <ProtectedRoute>
            <RestaurantvisitedPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/restaurantwrittenpage"
        element={
          <ProtectedRoute>
            <ReviewswrittenPage />
          </ProtectedRoute>
        }
      />

    </Routes>
  )
}

export default App