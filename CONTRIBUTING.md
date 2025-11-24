# Contributing Guide

Thank you for your interest in contributing to Dify EE (Enterprise Edition) Helm Chart Values Generator! 🎉

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or suggest features
- Provide clear descriptions, steps to reproduce, and relevant context
- Check existing issues before creating a new one

### Submitting Pull Requests

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**
   - Test the script with different configurations
   - Ensure backward compatibility

4. **Commit your changes**
   ```bash
   git commit -m "feat: add your feature description"
   ```
   - Use conventional commit messages (feat, fix, docs, refactor, etc.)

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Keep functions focused and small
- Add docstrings for public functions

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/dify-ee-helm-chart-values.git
cd dify-ee-helm-chart-values

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python generate-values-prd.py
```

## Documentation

- Update `README.md` for user-facing changes
- Update `docs/` for detailed documentation
- Keep `CHANGELOG.md` updated

## Questions?

Feel free to open an issue for any questions or discussions.

Thank you for contributing! 🙏

