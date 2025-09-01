# Contributing to The Kernel Toolkit (TKT)

Thank you for your interest in contributing to TKT! This document provides guidelines and information for contributors.

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Submission Guidelines](#submission-guidelines)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Community](#community)


## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Implement features or fix bugs
- **Documentation**: Improve guides, API docs, or examples
- **Testing**: Add test cases or test on new distributions
- **Distribution Support**: Add support for new Linux distributions

### Before You Start

1. **Check existing issues** to see if your contribution is already being discussed
2. **Create an issue** for significant changes to discuss the approach
3. **Fork the repository** and create a feature branch
4. **Review the codebase** to understand the architecture and patterns

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Linux system (or VM) for testing
- Text editor with Python support

### Environment Setup

1. **Fork and clone:**
```bash
git clone https://github.com/yourusername/TKT_Framework.git
cd TKT_Framework
```

2. **Create virtual environment:**
```bash
python -m venv tkt-dev
source tkt-dev/bin/activate  # Windows: tkt-dev\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -e .
pip install pytest pytest-cov black flake8 mypy pre-commit
```

4. **Set up pre-commit hooks:**
```bash
pre-commit install
```

5. **Verify setup:**
```bash
python -m TKT  # Should launch TKT
pytest         # Should run tests
```

## Submission Guidelines

### Issue Guidelines

#### Bug Reports

Use the bug report template and include:
- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details**: OS, Python version, TKT version
- **Error messages** and stack traces
- **Screenshots** if relevant

#### Feature Requests

Use the feature request template and include:
- **Clear description** of the proposed feature
- **Use case** and motivation
- **Proposed implementation** (if you have ideas)
- **Alternatives considered**
- **Additional context** or mockups

### Pull Request Guidelines

#### Before Submitting

- [ ] **Create an issue** first for significant changes
- [ ] **Write tests** for new functionality
- [ ] **Update documentation** as needed
- [ ] **Run the full test suite** locally
- [ ] **Follow code style** guidelines
- [ ] **Write clear commit messages**

#### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Related Issue
Closes #(issue number)

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change) 
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing on [distribution names]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No unnecessary dependencies added
```

### Branch Naming

Use descriptive branch names:
- `feature/add-fedora-support`
- `bugfix/fix-status-display`
- `docs/update-user-guide`
- `refactor/improve-error-handling`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(distro): add fedora package management support

- Implement FedoraConfigs class with dnf commands
- Add fedora to supported distributions list
- Update documentation with fedora installation notes

Closes #123
```

```
fix(ui): resolve status message not updating

The status label widget was not properly updating after
dependency installation due to widget mounting timing.

Fixes #456
```

## Coding Standards

### Python Style

Follow PEP 8 with these specifics:
- **Line length**: 88 characters (Black default)
- **Imports**: Grouped (stdlib, third-party, local)
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for all public APIs

### Code Quality Tools

We use these tools (run automatically via pre-commit):
- **Black**: Code formatting
- **Ruff**: Linting
- **MyPy**: Type checking
- **isort**: Import sorting

### Error Handling

- Use **specific exceptions** with descriptive messages
- **Handle expected errors** gracefully
- **Log errors** appropriately for debugging
- **Provide helpful user feedback**

Example:
```python
# Good
try:
    config = get_distro_configs(distro_name)
except ValueError as e:
    logger.error(f"Unsupported distribution: {distro_name}")
    return False, f"Distribution '{distro_name}' is not supported"

# Avoid
try:
    config = get_distro_configs(distro_name)
except Exception:
    return False, "Error"
```

### Documentation Standards

- **Docstrings**: All public functions, classes, and methods
- **Type hints**: All function parameters and returns
- **Comments**: Complex logic and non-obvious code
- **README updates**: For new features or changes

Example docstring:
```python
def install_dependencies(self) -> tuple[bool, str]:
    """
    Install required packages for kernel compilation.

    This method uses the distribution-specific package manager to install
    all necessary dependencies for compiling Linux kernels.

    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if installation succeeded, False otherwise
            - str: Status message describing the result

    Raises:
        RuntimeError: If distribution is not supported for package management.
        
    Example:
        >>> manager = TKTSystemManager()
        >>> success, message = manager.install_dependencies()
        >>> print(f"Success: {success}, Message: {message}")
    """
```

## Testing Requirements

### Test Coverage

- **New features**: Must include comprehensive tests
- **Bug fixes**: Must include regression tests
- **Coverage target**: Aim for >80% test coverage
- **Test types**: Unit tests, integration tests, UI tests

### Writing Tests

Use pytest with these patterns:

#### Unit Tests
```python
import pytest
from unittest.mock import patch, MagicMock
from TKT.cli import TKTSystemManager

class TestTKTSystemManager:
    def test_install_dependencies_success(self):
        """Test successful dependency installation."""
        manager = TKTSystemManager()
        manager.distro_supported = True
        manager.distro_config = MagicMock()
        
        success, message = manager.install_dependencies()
        assert success is True
        assert "successfully" in message.lower()

    @patch('TKT.cli.get_distribution_name')
    def test_unsupported_distribution(self, mock_get_distro):
        """Test handling of unsupported distribution."""
        mock_get_distro.side_effect = RuntimeError("Unsupported")
        
        manager = TKTSystemManager()
        assert manager.distro_supported is False
```

#### Integration Tests
```python
def test_full_dependency_installation_flow():
    """Test complete dependency installation process."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        
        manager = TKTSystemManager()
        success, message = manager.install_dependencies()
        
        assert success is True
        mock_run.assert_called()
```

### Running Tests

```bash
# Run all tests
make check

# Run with coverage
make coverage

# Run specific tests
make $test_name (lint, format, typecheck)

# Run integration tests only
make test
```

## Documentation

### Types of Documentation

1. **Code documentation**: Docstrings and comments
2. **User documentation**: User guide, installation instructions
3. **API documentation**: Module and class references  
4. **Developer documentation**: Architecture, contributing guides

### Documentation Updates

When contributing, update relevant documentation:

- **New features**: Add to user guide and API docs
- **Bug fixes**: Update troubleshooting sections
- **New distributions**: Add to supported list and installation notes
- **API changes**: Update API documentation and examples

### Documentation Style

- **Clear and concise**: Easy to understand
- **Examples**: Include code examples and usage
- **Structure**: Use consistent formatting and organization
- **Accuracy**: Keep documentation in sync with code

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions, ideas, and general discussion
- **Pull Requests**: Code review and collaboration

### Getting Help

- **Read the documentation**: User guide and API docs
- **Search existing issues**: Your question may already be answered
- **Ask in discussions**: For questions about usage or development
- **Create detailed issues**: For bugs or feature requests

### Review Process

1. **Automated checks**: CI/CD runs tests and code quality checks
2. **Code review**: Maintainers and community members review changes
3. **Discussion**: Questions and suggestions in PR comments
4. **Approval**: Changes approved by maintainers
5. **Merge**: Changes integrated into main branch

### Recognition

Contributors are recognized through:
- **GitHub contributors page**
- **Changelog mentions**
- **Thank you in releases**
- **Community acknowledgments**

## Distribution-Specific Contributions

### Adding New Distribution Support

This is a high-value contribution! Here's how to add support for a new Linux distribution:

#### 1. Research Phase
- **Package manager**: Identify the distribution's package manager
- **Package names**: Research equivalent packages for kernel development
- **Update commands**: Find repository update commands
- **Installation commands**: Identify package installation syntax

#### 2. Implementation Phase
- **Create config class**: Inherit from `DistroConfigs`
- **Implement methods**: `update_repos()` and `install_packages()`
- **Add to factory**: Register in `get_distro_configs()`
- **Update constants**: Add to `SUPPORTED_DISTROS`

#### 3. Testing Phase
- **Virtual machine**: Test on actual distribution
- **Package installation**: Verify all dependencies install correctly
- **Error handling**: Test failure scenarios
- **Integration**: Test with main TKT application

#### 4. Documentation Phase
- **Update README**: Add to supported distributions table
- **User guide**: Add distribution-specific instructions
- **Troubleshooting**: Add common issues and solutions

### Example Implementation

```python
class NewDistroConfigs(DistroConfigs):
    """Package management for NewDistro Linux."""
    
    newdistro_deps = [
        "kernel-devel",
        "gcc-toolset", 
        "development-tools"
    ]
    
    def __init__(self):
        self.packages = self.base_deps + self.newdistro_deps
    
    def update_repos(self):
        return self._run_command(
            ["sudo", "newpkg", "refresh"],
            "Updating NewDistro repositories"
        )
    
    def install_packages(self):
        return self._run_command(
            ["sudo", "newpkg", "install", "-y"] + self.packages,
            "Installing NewDistro packages"
        )
```

## Special Considerations

### Security

- **No hardcoded credentials**: Never commit secrets or API keys
- **Input validation**: Validate all user inputs
- **Command injection**: Use subprocess safely with list arguments
- **Privilege escalation**: Use sudo only when necessary

### Performance

- **Efficient algorithms**: Consider performance for large operations
- **Resource usage**: Monitor memory and CPU usage
- **Caching**: Cache expensive operations when appropriate
- **Async operations**: Consider async for long-running tasks

### Compatibility

- **Python versions**: Support Python 3.11+
- **Distribution compatibility**: Test on target distributions
- **Dependency versions**: Use compatible version ranges
- **Backward compatibility**: Avoid breaking changes when possible

## Release Contributions

### Beta Testing

Help test pre-release versions:
- **Install beta versions** on various distributions
- **Report issues** found during testing
- **Verify bug fixes** work as expected
- **Test new features** thoroughly

### Translation (Future)

When internationalization is added:
- **Translate messages** to your language
- **Review translations** for accuracy
- **Test UI** with translated text
- **Maintain translations** as code evolves

## Mentorship and Learning

### New Contributors

We welcome new contributors! If you're new to open source:
- **Start small**: Look for "good first issue" labels
- **Ask questions**: Don't hesitate to ask for help
- **Learn by doing**: Contribute what you can, learn as you go
- **Review others' PRs**: Great way to learn the codebase

### Experienced Contributors

Help mentor new contributors:
- **Review pull requests** constructively
- **Answer questions** in discussions
- **Create "good first issue"** opportunities
- **Share knowledge** about the codebase

## Project Governance

### Decision Making

- **Technical decisions**: Discussed in GitHub issues/discussions
- **Architecture changes**: Require broader community input
- **Breaking changes**: Carefully considered and well-communicated
- **Feature priorities**: Based on community needs and maintainer capacity

### Maintainer Responsibilities

Maintainers are responsible for:
- **Code review**: Ensuring quality and consistency
- **Release management**: Planning and executing releases
- **Issue triage**: Organizing and prioritizing issues
- **Community management**: Fostering a welcoming environment
- **Direction setting**: Guiding project evolution

## Recognition and Attribution

### Contributors

All contributors are recognized through:
- **GitHub contributors graph**
- **CONTRIBUTORS.md file** (when created)
- **Release notes** mentioning significant contributions
- **Documentation acknowledgments**

### Types of Contributions Recognized

- Code contributions (features, fixes, refactoring)
- Documentation improvements
- Bug reports and testing
- Design and UX feedback
- Community support and mentoring
- Translation work (future)

## Getting Started Checklist

For your first contribution:

- [ ] **Read this contributing guide** thoroughly
- [ ] **Set up development environment** following the instructions
- [ ] **Run the test suite** to ensure everything works
- [ ] **Find an issue to work on** or create a new one
- [ ] **Fork the repository** and create a feature branch
- [ ] **Make your changes** following the coding standards
- [ ] **Write tests** for your changes
- [ ] **Update documentation** as needed
- [ ] **Run pre-commit hooks** and fix any issues
- [ ] **Submit a pull request** with a clear description
- [ ] **Respond to feedback** during the review process

## Questions?

If you have questions about contributing:

1. **Check existing documentation** first
2. **Search closed issues** for similar questions
3. **Ask in GitHub Discussions** for general questions
4. **Create an issue** for specific problems or suggestions
5. **Join community discussions** to connect with other contributors

## Thank You!

Your contributions help make TKT better for everyone. Whether you're fixing a typo, adding a feature, or helping other users, every contribution is valuable and appreciated.

We look forward to working with you!

---

*This contributing guide is a living document. If you find ways to improve it, please submit a pull request!*
