The goal of App.test.jsx is to:
•	Confirm that each route (/login, /signup, /home/:id, /restaurant/:id) loads the correct component.
•	Test routing behavior without starting the actual app in the browser.
•	Validate integration between:
    o	React Router
    o	App.jsx routing structure
    o	ProtectedRoute wrapper logic
•	Ensure components render correctly when routed using MemoryRouter.

Testing Tools
•	Jest — test runner + mocking framework
•	React Testing Library — rendering + asserting UI output
•	MemoryRouter — simulates browser navigation for tests


