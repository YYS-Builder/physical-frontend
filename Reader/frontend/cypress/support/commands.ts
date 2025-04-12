/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable<Subject = any> {
    /**
     * Custom command to check if elements are sorted
     * @example cy.get('.items').should('be.sorted', { key: 'text' })
     */
    'be.sorted': (options: { key: string; order?: 'asc' | 'desc' }) => Chainable<Subject>
  }
}

Cypress.Commands.add('be.sorted', { prevSubject: true }, (subject: JQuery<HTMLElement>, options: { key: string; order?: 'asc' | 'desc' }) => {
  const { key, order = 'asc' } = options
  const elements = subject.toArray()
  const values = elements.map(el => Cypress.$(el).find(key).text().trim())
  const sortedValues = [...values].sort((a, b) => {
    if (order === 'asc') {
      return a.localeCompare(b)
    }
    return b.localeCompare(a)
  })

  expect(values).to.deep.equal(sortedValues)
  return subject
}) 