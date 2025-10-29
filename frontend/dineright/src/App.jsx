import React from 'react'
import LoginPage from './features/auth/pages/loginpage'
import SignUpPage from './features/auth/pages/signuppage'
import PreferencePage from './features/auth/pages/Preferencepage';
import { Routes, Route } from "react-router-dom";
import ProtectedRoute from "./features/auth/components/routing/ProtectedRoute.jsx";
import HomePage from './features/home/pages/HomePage.jsx';
import MyCornerPage from './features/home/pages/MyCornerPage.jsx';
const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/preferences" element={<PreferencePage />} />
      <Route
        path="/home"
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

    </Routes>
  )
}

export default App