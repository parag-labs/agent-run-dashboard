# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project uses [semantic versioning](https://semver.org/).

## [Unreleased]

### Changed

- Backend now targets Python 3.14 (was 3.11; 3.15 waits on pydantic-core wheels); frontend targets Node.js 26 LTS (CI was on Node 20).
- CI uses `actions/checkout`, `actions/setup-python`, and `actions/setup-node` v7, reading versions from `backend/.python-version` and `frontend/.nvmrc`.

## [0.1.0] - 2026-09-07

First public release. FastAPI + SQLite backend with token auth and a React dashboard for recording agent runs and their cost, tokens, and failures.

[0.1.0]: https://github.com/parag-labs/agent-run-dashboard/releases/tag/v0.1.0
