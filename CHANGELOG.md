# Changelog

## [0.1.0-integrated] - 2025-??-??
### Added
- `redmane/auxiliary.py`: Single-pass scanning logic.
- `update_local.py`: Wrapper script for backward compatibility.
- `demo/`: Demo dataset with valid config.
- `test_imaging/`, `test_WGS/`: Placeholder tests.

### Changed
- `redmane/generator.py`: Refactored to use `auxiliary`.
- `redmane/config.py`: Enforced STRICT validation (fail loudly).
- `README.md`: Updated with package and CLI usage instructions.
- `.gitignore`: Excluded generated artifacts.

### Removed
- Default file extensions (moved to strict `config.json`).
