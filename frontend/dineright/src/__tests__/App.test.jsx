import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

// Mock components 
jest.mock("../features/auth/pages/LoginPage.jsx", () => () => <div>Login Page</div>);
jest.mock("../features/auth/pages/SignUpPage.jsx", () => () => <div>Sign Up Page</div>);
jest.mock("../features/auth/pages/PreferencePage.jsx", () => () => <div>Preference Page</div>);
jest.mock("../features/home/pages/HomePage.jsx", () => () => <div>Home Page</div>);
jest.mock("../features/home/pages/MyCornerPage.jsx", () => () => <div>My Corner Page</div>);
jest.mock("../features/home/pages/RestaurantPage.jsx", () => () => <div>Restaurant Page</div>);
jest.mock("../features/home/pages/RestaurantvisitedPage.jsx", () => () => <div>Visited Page</div>);
jest.mock("../features/home/pages/ReviewswrittenPage.jsx", () => () => <div>Written Page</div>);

// Mock ProtectedRoute
jest.mock("../features/auth/components/routing/ProtectedRoute.jsx", () => {
  return ({ children }) => <div>Protected: {children}</div>;
});


describe("App Routing", () => {

  test("renders Login page when navigating to /login", () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  test("renders SignUp page when navigating to /signup", () => {
    render(
      <MemoryRouter initialEntries={["/signup"]}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText("Sign Up Page")).toBeInTheDocument();
  });

  test("renders HomePage inside ProtectedRoute", () => {
    render(
      <MemoryRouter initialEntries={["/home/123"]}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText("Protected:")).toBeInTheDocument();
    expect(screen.getByText("Home Page")).toBeInTheDocument();
  });

  test("renders Restaurant page inside ProtectedRoute", () => {
    render(
      <MemoryRouter initialEntries={["/restaurant/10"]}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText("Protected:")).toBeInTheDocument();
    expect(screen.getByText("Restaurant Page")).toBeInTheDocument();
  });

});
