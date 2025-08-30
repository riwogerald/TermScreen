# Terminal Screen Renderer - Development Makefile

.PHONY: help install install-dev test test-verbose test-coverage clean format lint demo benchmark docs

# Default target
help:
	@echo "Terminal Screen Renderer - Development Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup:"
	@echo "  install      Install the package"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests"
	@echo "  test-verbose Run tests with verbose output"
	@echo "  test-coverage Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  format       Format code with black"
	@echo "  lint         Run code linting"
	@echo ""
	@echo "Demos:"
	@echo "  demo         Run interactive demo"
	@echo "  demo1        Run demo 1"
	@echo "  demo2        Run demo 2"
	@echo ""
	@echo "Performance:"
	@echo "  benchmark    Run performance benchmarks"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Clean up generated files"
	@echo "  docs         Generate documentation"

# Installation
install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:
	python run_all_tests.py

test-verbose:
	python test_renderer.py -v
	python test_performance.py -v
	python test_integration.py -v

test-coverage:
	coverage run --source=. -m pytest test_*.py
	coverage report -m
	coverage html

# Code quality
format:
	black *.py --line-length 100
	@echo "Code formatting complete!"

lint:
	flake8 *.py --max-line-length=100 --ignore=E203,W503
	mypy *.py --ignore-missing-imports
	@echo "Linting complete!"

# Demos
demo:
	@echo "Choose a demo:"
	@echo "1. Basic demo with text and shapes"
	@echo "2. Pattern demo with checkerboard"
	@read -p "Enter demo number (1 or 2): " demo && python demo.py $$demo | python renderer.py

demo1:
	python demo.py 1 | python renderer.py

demo2:
	python demo.py 2 | python renderer.py

# Performance
benchmark:
	@echo "Running performance benchmarks..."
	python test_performance.py
	@echo "Benchmark complete!"

# Documentation
docs:
	@echo "Generating documentation..."
	python -c "import renderer, demo; help(renderer); help(demo)" > docs/api.txt
	@echo "Documentation generated in docs/"

# Maintenance
clean:
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "Cleanup complete!"

# Build and distribution
build:
	python setup.py sdist bdist_wheel
	@echo "Build complete! Check dist/ folder"

upload-test:
	twine upload --repository testpypi dist/*

upload:
	twine upload dist/*
