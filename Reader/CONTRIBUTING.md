# Contributing to Reader

Thank you for your interest in contributing to Reader! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the [issue tracker](https://github.com/your-username/reader/issues).
2. If not, create a new issue with:
   - A clear, descriptive title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots if applicable
   - Environment details

### Suggesting Features

1. Check if the feature has already been suggested.
2. Create a new issue with:
   - A clear, descriptive title
   - Detailed description
   - Use cases
   - Potential implementation ideas
   - Screenshots or mockups if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes
4. Commit your changes:
   ```bash
   git commit -m 'feat: add amazing feature'
   ```
5. Push to your fork:
   ```bash
   git push origin feature/amazing-feature
   ```
6. Open a pull request

## Development Setup

### Prerequisites

- Node.js 18.x
- Python 3.11
- PostgreSQL 15
- Redis 7
- Docker and Docker Compose

### Installation

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/reader.git
   cd reader
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the development servers:
   ```bash
   # Backend
   cd backend
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

## Coding Standards

### Frontend

- Use Vue 3 Composition API
- Follow TypeScript best practices
- Use ESLint and Prettier
- Write unit tests for components
- Follow accessibility guidelines

### Backend

- Follow PEP 8 style guide
- Use type hints
- Write docstrings
- Add unit tests
- Handle errors appropriately

## Testing

### Frontend Tests

Run tests:
```bash
cd frontend
npm test
```

Test coverage:
```bash
npm run test:coverage
```

### Backend Tests

Run tests:
```bash
cd backend
pytest
```

Test coverage:
```bash
pytest --cov=src
```

## Documentation

- Update documentation when adding features
- Follow the existing documentation style
- Include code examples
- Add comments for complex logic

## Pull Request Process

1. Ensure tests pass
2. Update documentation
3. Add changelog entry
4. Request review
5. Address feedback
6. Merge after approval

## Release Process

1. Create release branch
2. Update version
3. Update changelog
4. Run tests
5. Build artifacts
6. Deploy
7. Tag release

## Getting Help

- GitHub Issues
- Discord channel
- Documentation
- Code examples

## Recognition

Contributors will be:
- Listed in the README
- Acknowledged in release notes
- Given commit access for significant contributions

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 