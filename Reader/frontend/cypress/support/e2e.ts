import '@testing-library/cypress/add-commands';

// Custom commands
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login');
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
});

Cypress.Commands.add('logout', () => {
  cy.get('[data-testid="user-menu"]').click();
  cy.get('[data-testid="logout-button"]').click();
});

Cypress.Commands.add('createCollection', (name: string, description: string) => {
  cy.get('[data-testid="create-collection"]').click();
  cy.get('input[name="name"]').type(name);
  cy.get('textarea[name="description"]').type(description);
  cy.get('button[type="submit"]').click();
});

Cypress.Commands.add('uploadDocument', (filePath: string) => {
  cy.get('[data-testid="upload-document"]').click();
  cy.get('input[type="file"]').attachFile(filePath);
  cy.get('button[type="submit"]').click();
});

// Custom assertions
Cypress.Commands.add('shouldHaveAnalytics', () => {
  cy.get('[data-testid="analytics-dashboard"]').should('exist');
  cy.get('[data-testid="total-documents"]').should('exist');
  cy.get('[data-testid="reading-time"]').should('exist');
  cy.get('[data-testid="reading-speed"]').should('exist');
  cy.get('[data-testid="completion-rate"]').should('exist');
});

// Global configurations
beforeEach(() => {
  // Clear localStorage and sessionStorage
  cy.clearLocalStorage();
  cy.clearSessionStorage();
  
  // Set default viewport
  cy.viewport(1280, 720);
});

afterEach(() => {
  // Take screenshot on failure
  if (Cypress.currentTest.state === 'failed') {
    cy.screenshot();
  }
}); 