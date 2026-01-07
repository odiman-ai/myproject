// .eslintrc.js
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
  ],
  parserOptions: {
    ecmaFeatures: { jsx: true },
    ecmaVersion: 2021,
    sourceType: "module",
  },
  plugins: ["react"],
  rules: {
    // your project rules
  },
  overrides: [
    {
      files: ["**/*.test.{js,jsx}", "**/*.spec.{js,jsx}", "cypress/**/*.js", "cypress/**/*.cy.{js,jsx,ts,tsx}"],
      env: {
        jest: true,
        "cypress/globals": true,
      },
      plugins: ["cypress"],
    },
    {
      files: ["cypress/**/*.cy.{js,jsx,ts,tsx}"],
      env: { mocha: true, "cypress/globals": true },
    },
  ],
};
