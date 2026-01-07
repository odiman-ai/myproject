// cypress.config.js
const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: "http://127.0.0.1:8000", // backend base for API requests
    specPattern: "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: false, // set to "cypress/support/e2e.js" if you add support
    setupNodeEvents(on, config) {
      // you can add node event handlers here if needed
      return config;
    },
  },

  component: {
    // pattern for component specs (keep separate from e2e)
    specPattern: "cypress/component/**/*.cy.{js,jsx,ts,tsx}",

    // Vite + React dev server for component testing
    devServer: {
      framework: "react",
      bundler: "vite",
    },
  },
});
