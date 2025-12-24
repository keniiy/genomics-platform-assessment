.PHONY: format type-check test clean install install-dev

# Format code
format:
	black handler.py tests/
	isort handler.py tests/

# Type checking
type-check:
	mypy handler.py

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=handler --cov-report=term-missing

# Install production dependencies
install:
	pip install -r requirements.txt -t .

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt

# Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	rm -f .coverage

# Build deployment package
package: clean install
	zip -r deployment.zip . -x "*.pyc" "__pycache__/*" "*.git*" "README.md" "tests/*" "*.toml" "Makefile" "requirements-dev.txt" ".pytest_cache/*" ".mypy_cache/*"

