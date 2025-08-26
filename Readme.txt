📌 Overview

This repository contains my implementation of Miguel Grinberg’s Flask Mega-Tutorial project.
The application is a microblogging platform built with Flask, SQLAlchemy, Jinja2, and related tools.

The purpose of this repo is to showcase the codebase — not to provide a production-ready deployment. While most of the application works as intended, there are a few limitations due to the hybrid development environment I used.

✅ What Works

User authentication (register, login, logout)

Post creation and display

Pagination of posts

User profile pages (viewing posts by user)

Following/unfollowing users

Error handling with custom templates

Notifications system (at the database + template level)

Multi-language support scaffolding (via Flask-Babel)

Dockerfile for containerization

⚠️ What Doesn’t Fully Work

Because of how the project was built across Windows + WSL (Linux VM), some functions require local services that aren’t running in production:

Background Jobs (Redis + RQ)

Redis Queue workers were set up under WSL (Linux).

These jobs won’t process in a fresh environment without Redis installed and configured.

Search (Elasticsearch)

Elasticsearch was hosted locally on Windows.

Indexing/search functionality won’t work without a live Elasticsearch service running.

Hybrid Environment Limitations

Some commands and scripts were run from WSL (Ubuntu) using Linux CLI tools.

Other parts (e.g., Docker Desktop, VS Code) ran directly on Windows.

This hybrid workflow means the app isn’t immediately portable without adjustments.

🖥️ Environment Details

Windows 10/11 Host with Docker Desktop

WSL2 (Ubuntu 22.04) for running Flask, Redis, and CLI tools

Python 3.12 (WSL) inside virtual environments (venv/)

Postgres/SQLite for database backends (depending on stage of tutorial)

Redis running under WSL

Elasticsearch running natively on Windows

🔒 What I’ve Cleaned Up

Added .gitignore to exclude sensitive files (.env, venv/, .vscode/, __pycache__/).

Removed committed secrets (Azure Translator key, etc.) from repo history.

This repo is safe for public review.

📚 Notes

This project was primarily a learning exercise.

The architecture and code are solid, but a few services are intentionally not running because they were tied to my local dev setup.

If you want to run this end-to-end, you’ll need to spin up Redis, Elasticsearch, and configure environment variables yourself.

📎 Final Thoughts

This repo is intended as a read-only showcase of my work completing the Flask tutorial.
It demonstrates my ability to:

Debug across a hybrid Windows/Linux stack

Configure and integrate third-party services

Manage virtual environments and containers

Resolve GitHub push protection issues (secrets cleanup, history rewrites)

While not production-deployed, the code is complete, clean, and ready to be reviewed.
