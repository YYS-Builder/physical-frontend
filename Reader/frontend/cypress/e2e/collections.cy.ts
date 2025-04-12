describe('Collections', () => {
  beforeEach(() => {
    cy.visit('/collections')
  })

  it('should display collections list', () => {
    cy.get('.collection-list').should('exist')
    cy.get('.collection-card').should('have.length.at.least', 1)
  })

  it('should create a new collection', () => {
    cy.get('.btn-create').click()
    cy.get('.modal').should('be.visible')

    cy.get('input[name="name"]').type('Test Collection')
    cy.get('textarea[name="description"]').type('Test Description')
    cy.get('select[name="privacy"]').select('private')

    cy.get('.btn-save').click()
    cy.get('.modal').should('not.exist')
    cy.contains('Test Collection').should('exist')
  })

  it('should edit a collection', () => {
    cy.get('.collection-card').first().find('.btn-edit').click()
    cy.get('.modal').should('be.visible')

    cy.get('input[name="name"]').clear().type('Updated Collection')
    cy.get('textarea[name="description"]').clear().type('Updated Description')
    cy.get('select[name="privacy"]').select('public')

    cy.get('.btn-save').click()
    cy.get('.modal').should('not.exist')
    cy.contains('Updated Collection').should('exist')
  })

  it('should delete a collection', () => {
    cy.get('.collection-card').first().find('.btn-delete').click()
    cy.get('.modal').should('be.visible')
    cy.contains('Are you sure you want to delete this collection?').should('exist')

    cy.get('.btn-confirm').click()
    cy.get('.modal').should('not.exist')
    cy.contains('Collection deleted successfully').should('exist')
  })

  it('should filter collections', () => {
    cy.get('.search-input').type('Test')
    cy.get('.collection-card').should('have.length.at.least', 1)
    cy.get('.collection-card').each($card => {
      cy.wrap($card).find('h3').should('contain.text', 'Test')
    })

    cy.get('.filter-select').first().select('name')
    cy.get('.collection-card').should('be.sorted', { key: 'h3' })

    cy.get('.filter-select').last().select('private')
    cy.get('.collection-card').each($card => {
      cy.wrap($card).find('.privacy-badge').should('contain.text', 'Private')
    })
  })

  it('should handle empty state', () => {
    cy.get('.search-input').type('NonExistentCollection')
    cy.get('.empty-state').should('exist')
    cy.contains('No collections found').should('exist')
  })
}) 