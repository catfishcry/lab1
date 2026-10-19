# Lab1 Secure REST API
## Project & API description
Technology stack: Python Flask + SQLite + SQLAlchemy ORM
Endpoints:
1. POST /auth/register
- Input JSON: {"username":"xxx","password":"xxx"}
- Register new user, store bcrypt hashed password. Return 201 when success.

2. POST /auth/login
- Input JSON: {"username":"xxx","password":"xxx"}
- Return JWT access‑token for authenticated users.

3. GET /api/data
- Protected endpoint, Header: Authorization: Bearer <token>
- Return list of users.

## Implemented security measures
1. SQL Injection protection:
Use SQLAlchemy ORM, no manual string concatenation for SQL queries. ORM automatically uses parameterized prepared statements.

2. XSS protection:
Use markupsafe.escape() function to escape all user‑origin output data before returning in JSON responses.

3. Broken Authentication protection:
- Passwords are stored as bcrypt hash, never plaintext.
- After successful login, server issues JWT token with expiration time.
- Custom token_required middleware validates JWT on every protected API call. Access is denied without valid token.

## SAST & SCA scan reports
*(粘贴GitHub Actions截图)*

## Selected CVE information
CVE‑ID: CVE‑2019‑10906 Flask Jinja2 SSTI
Brief description: Jinja2 template render function allows remote code execution if untrusted user input passed to render_string().

## CVE reproduction steps
*(命令、截图)*

## Root‑cause analysis
*(根因分析)*

## Applied fix description
*(修复描述)*

## Proof of fix
*(修复验证截图)*
