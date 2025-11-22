# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.8] - 2025-11-22

### Added
- Support for parsing the new **REWE Bonus** loyalty program, including earned credit and value-based coupons.
- New test suite to validate REWE Bonus parsing logic.
- The `loyaltyProgramQualified` column in CSV table exports now holds the loyalty program name (or is empty when the item is not qualified).
- CSV exports now include `market`, `marketStreet`, `marketZip`, and `marketCity` columns so each row carries its originating store information.


### Changed
- **[BREAKING CHANGE]** The top-level `payback` key in the JSON output has been replaced by a generalized `loyalty` object. This new object specifies the `program` ("PAYBACK" or "REWE Bonus") and contains the program-specific `details`.
- **[BREAKING CHANGE]** In the `items` list, the `paybackQualified` boolean field has been replaced with the `loyaltyProgramQualified` string field, which holds the name of the qualifying program or is `null`.
- Renamed internal data class `PaybackData` to `PaybackDetails` for clarity within the new loyalty model.

### Fixed
- Improved parser stability by pre-scanning for the loyalty program type before processing items, ensuring correct qualification labeling.

## [0.0.7] - 2024-08-08

### Added
- Add docs

## [0.0.6] - 2024-08-04

### Added
- Added `--csv-table` functionality to parse items from PDF or JSON files and save them into a single CSV table.
- Added basic documentation in docstrings
- Fix issues with parsing addresses from certain receipts.

## [0.0.5] - 2024-08-04

### Added
- Initial release of the `rewe-ebon-parser` package.
