# Contributing to agent-memory-layer

Thanks for your interest in contributing! This document covers the basics.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/agent-memory-layer.git
   cd agent-memory-layer
   ```
3. **Install** development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. **Run** tests to ensure everything works:
   ```bash
   pytest
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes with appropriate tests
3. Run the test suite before committing:
   ```bash
   pytest -v
   ```
4. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` — new feature
   - `fix:` — bug fix
   - `docs:` — documentation only
   - `test:` — adding or updating tests
   - `chore:` — maintenance tasks

5. Push and open a Pull Request

## Adding a New Component

When implementing a new pluggable component (e.g., a new VectorStore), follow these steps:

1. Implement the interface defined in `core.py`
2. Add tests in `tests/test_<component>.py`
3. Update `README.md` component table
4. Update `CHANGELOG.md`

## Reporting Issues

Before opening an issue:
- Search existing issues
- Include your environment (Python version, OS)
- Provide a minimal reproducible example if applicable

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
