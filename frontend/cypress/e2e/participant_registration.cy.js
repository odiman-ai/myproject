// cypress/e2e/participant_registration.cy.js

describe("Participant registration flow", () => {
  let token;  // <-- declare here

  const API = Cypress.env("API_BASE") || "http://127.0.0.1:8000";

  before(() => {
    cy.request({
      method: "POST",
      url: `${API}/login`,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: {
        username: Cypress.env("ADMIN_USERNAME") || "admin",
        password: Cypress.env("ADMIN_PASSWORD") || "admin123"
      }
    }).then((resp) => {
      expect(resp.status).to.eq(200);
      expect(resp.body).to.have.property("access_token");
      token = resp.body.access_token;   // now valid
    });
  });

  it("creates a participant successfully (happy path)", () => {
    const payload = {
      name: "Cypress Participant",
      gender: "male",
      age: 35,
      location: "Gulu",
      national_id: `CYP-${Date.now()}`
    };

    cy.request({
      method: "POST",
      url: `${API}/participants`,
      headers: { Authorization: `Bearer ${token}` },
      body: payload
    }).then((resp) => {
      expect(resp.status).to.be.oneOf([200, 201]);
      expect(resp.body).to.have.property("id");
      cy.wrap(resp.body.id).as("participantId");
    });
  });

  it("retrieves the created participant", function () {
    cy.get("@participantId").then((id) => {
      cy.request({
        method: "GET",
        url: `${API}/participants/${id}`,
        headers: { Authorization: `Bearer ${token}` }
      }).then((resp) => {
        expect(resp.status).to.eq(200);
        expect(resp.body).to.have.property("id", id);
      });
    });
  });
});
