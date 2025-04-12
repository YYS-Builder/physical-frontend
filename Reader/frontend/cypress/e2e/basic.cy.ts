describe('Basic App Tests', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should load the home page', () => {
    cy.get('h1').should('exist')
  })

  it('should have a working navigation', () => {
    cy.get('nav').should('exist')
    cy.get('nav a').should('have.length.at.least', 1)
  })
}) 