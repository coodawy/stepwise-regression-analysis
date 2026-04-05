# Contributing to Stepwise Regression Analysis

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## 🐛 Reporting Bugs

If you find a bug, please create an issue on GitHub with:

- **Clear title**: Describe the issue concisely
- **Description**: What happened vs. what you expected
- **Steps to reproduce**: Minimal code example
- **Environment**: Python version, OS, package versions
- **Error messages**: Full traceback if applicable

## 💡 Suggesting Features

Feature suggestions are welcome! Please create an issue with:

- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches you've considered
- **Examples**: Code examples if applicable

## 🔧 Code Contributions

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/stepwise-regression-analysis.git
cd stepwise-regression-analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to all functions
- Keep functions focused and modular
- Maximum line length: 100 characters

### Testing

Before submitting a pull request:

```bash
# Run tests
pytest tests/

# Check code style
flake8 src/

# Format code
black src/
```

### Pull Request Process

1. **Create a branch**: `git checkout -b feature/your-feature-name`
2. **Make changes**: Implement your feature or fix
3. **Test thoroughly**: Ensure all tests pass
4. **Update documentation**: Update README.md if needed
5. **Commit**: Use clear, descriptive commit messages
6. **Push**: `git push origin feature/your-feature-name`
7. **Create PR**: Submit pull request with description

### Commit Message Format

```
type: brief description

Detailed explanation of changes (if needed)

Fixes #issue-number
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 📚 Documentation

Improvements to documentation are always welcome:

- Fix typos or unclear explanations
- Add examples or tutorials
- Improve API documentation
- Translate documentation

## 🔬 Research Collaboration

For research collaborations or academic partnerships:

**Contact**: Abdulrahman Hussein  
**Email**: ahusse12@kent.edu  
**ORCID**: [0009-0003-0401-9219](https://orcid.org/0009-0003-0401-9219)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- CHANGELOG.md for specific contributions
- GitHub contributors page

Thank you for helping improve this project!
