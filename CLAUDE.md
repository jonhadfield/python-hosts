# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- `python3 -m pytest -vv --cov=python_hosts --cov-report=term-missing --cov-report=xml --cov-report=html --cov-fail-under=90 --cov-branch --junitxml=pytest.xml` - Run tests with coverage (90% minimum)
- `make test` - Alternative test command (note: currently has incorrect --cov=ipq flag, should be --cov=python_hosts)
- `python setup.py test` - Legacy test runner using pytest

### Code Quality
- `ruff check . --ignore E501,F401` - Run linting (ignores line length and unused imports)
- `make lint` - Alternative lint command

### Environment Setup
- `python3 -m pip install -r test-requirements.txt` - Install test dependencies
- `make setup` - Setup development environment

### Build and Distribution
- `python setup.py sdist` - Build source distribution
- `make build-docker` - Build Docker image
- `tox` - Run tests across multiple Python versions (2.7, 3.8-3.11)

### Documentation
- `cd docs && make html` - Build HTML documentation with Sphinx
- `cd docs && make clean` - Clean documentation build files
- `cd docs && make linkcheck` - Check documentation links
- `cd docs && make coverage` - Generate documentation coverage report
- Documentation output in `docs/_build/html/`

## Architecture

This is a Python library for managing hosts files (`/etc/hosts` on Unix, `C:\Windows\System32\drivers\etc\hosts` on Windows).

### Core Classes

**`HostsEntry`** (`python_hosts/hosts.py`):
- Represents a single line in a hosts file
- Entry types: `ipv4`, `ipv6`, `comment`, `blank`
- Main attributes: `entry_type`, `address`, `comment`, `names`
- Uses `__slots__` for memory efficiency

**`Hosts`** (`python_hosts/hosts.py`):
- Represents an entire hosts file
- Manages collections of `HostsEntry` objects
- Supports reading from file paths or URLs
- Provides methods for adding, removing, and writing entries

### Key Features
- Import entries from files or URLs (e.g., `hosts.import_url()`)
- Add/remove individual entries or batches
- Validate IPv4/IPv6 addresses and hostnames
- Handle comments and blank lines
- Support for duplicate name detection with `allow_name_dupliction` parameter
- **Unicode Support**: Full Unicode support for hostnames and comments (Python 2.7 & 3.x compatible)
- **IDN Support**: Automatic conversion of internationalized domain names to ASCII-compatible encoding

### Module Structure
- `python_hosts/hosts.py` - Main classes (`Hosts`, `HostsEntry`)
- `python_hosts/utils.py` - Utility functions for validation (`is_ipv4`, `is_ipv6`, `valid_hostnames`)
- `python_hosts/exception.py` - Custom exceptions (`HostsException`, `InvalidIPv4Address`, etc.)
- `python_hosts/unicode_utils.py` - Unicode compatibility utilities for Python 2/3 support
- `python_hosts/__init__.py` - Package exports

### Testing
- Tests use `pytest` with `tmpdir` fixture for temporary file creation
- Test files located in `tests/` directory
- Sample hosts files in `test_files/` for testing various formats
- Coverage reporting configured for 90% minimum coverage