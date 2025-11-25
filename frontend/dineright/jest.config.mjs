export default {
  testEnvironment: "jsdom",

  setupFiles: ["<rootDir>/jest.polyfills.cjs"],

  setupFilesAfterEnv: ["@testing-library/jest-dom"],

  transform: {
    "^.+\\.(js|jsx)$": "babel-jest",
  },

  moduleFileExtensions: ["js", "jsx"],

  moduleNameMapper: {
    "\\.(css|less|scss)$": "identity-obj-proxy",
  },
};
