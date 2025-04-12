describe('Analytics Dashboard', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123');
    cy.visit('/analytics');
  });

  it('displays analytics dashboard with correct data', () => {
    cy.shouldHaveAnalytics();
    
    // Check summary cards
    cy.get('[data-testid="total-documents"]').should('contain', '10');
    cy.get('[data-testid="reading-time"]').should('contain', '2h 0m');
    cy.get('[data-testid="reading-speed"]').should('contain', '200 wpm');
    cy.get('[data-testid="completion-rate"]').should('contain', '75%');
  });

  it('changes date range and updates data', () => {
    // Select 7 days range
    cy.get('[data-testid="date-range"]').select('7');
    
    // Check if data is updated
    cy.get('[data-testid="total-documents"]').should('not.contain', '10');
  });

  it('exports analytics data', () => {
    cy.get('[data-testid="export-data"]').click();
    
    // Check if download started
    cy.window().then((win) => {
      const downloadStarted = win.performance.getEntriesByType('resource')
        .some((entry) => entry.name.includes('analytics.csv'));
      expect(downloadStarted).to.be.true;
    });
  });

  it('displays loading state', () => {
    // Mock slow response
    cy.intercept('GET', '/api/analytics', {
      delay: 1000,
      body: {},
    }).as('getAnalytics');

    cy.visit('/analytics');
    cy.get('[data-testid="loading-spinner"]').should('be.visible');
    cy.wait('@getAnalytics');
    cy.get('[data-testid="loading-spinner"]').should('not.exist');
  });

  it('handles error state', () => {
    // Mock error response
    cy.intercept('GET', '/api/analytics', {
      statusCode: 500,
      body: { error: 'Failed to fetch analytics' },
    }).as('getAnalytics');

    cy.visit('/analytics');
    cy.wait('@getAnalytics');
    cy.get('[data-testid="error-message"]').should('contain', 'Failed to fetch analytics');
  });

  it('navigates to document analytics', () => {
    cy.get('[data-testid="top-documents"]').first().click();
    cy.url().should('include', '/documents/');
    cy.get('[data-testid="document-analytics"]').should('exist');
  });
}); 