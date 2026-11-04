# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project uses [semantic versioning](https://semver.org/).

## [Unreleased]

### Changed

- Backend now targets Python 3.14 (was 3.11; 3.15 waits on pydantic-core wheels); frontend targets Node.js 26 LTS (CI was on Node 20).
- CI uses `actions/checkout`, `actions/setup-python`, and `actions/setup-node` v7, reading versions from `backend/.python-version` and `frontend/.nvmrc`.
- Frontend upgraded to React 19, Vite 8 (with `@vitejs/plugin-react` 6), Vitest 5, TypeScript 6.0, jsdom 30, and `@testing-library/jest-dom` 7. TypeScript stays on 6.0 because typescript-eslint doesn't support 7 yet.
- ESLint upgraded to 10; the legacy `.eslintrc.json` is replaced by a flat `eslint.config.js` using the `typescript-eslint` package, with the same rules.
- Backend dependency floors raised to current releases (FastAPI 0.162, SQLModel 0.0.48, Uvicorn 0.54, pytest 9.2). Tests use `httpx2`, which Starlette now prefers over `httpx` for its `TestClient`.

## [0.1.0] - 2026-09-07

First public release. FastAPI + SQLite backend with token auth and a React dashboard for recording agent runs and their cost, tokens, and failures.

[0.1.0]: https://github.com/parag-labs/agent-run-dashboard/releases/tag/v0.1.0
