# Cundamanix Static Analysis

Minimal quick start and essential notes.

Quick start (Docker)
- Build & run:
  ```bash
  docker compose build --no-cache
  docker compose up --build -d
  ```
- App URL: http://localhost:5001

Default credentials
- Username: mobsf
- Password: mobsf

API (permissions-only PDF)
- POST /api/v1/permissions_pdf
- Body: JSON { "hash": "<apk_or_ipa_hash>" }
- Header: Authorization: <api_key>

Troubleshooting (short)
- If container keeps restarting, check: `docker compose logs -f mobsf`.
- If `clean.sh` is missing, your `docker-compose.yaml` likely mounts `./src` and overwrote `/app/src` in the image. Either remove the mount or ensure `./src` contains project files.
- MobSF needs Java 8+ and wkhtmltopdf. If you see `JDK 8+ is not available` or PDF errors, ensure the Docker image installs OpenJDK and wkhtmltopdf.
- To reset (clean) DB/uploads once: `docker compose run --rm -e RUN_CLEAN=true mobsf`.

Further details (development, debugging) are in project files and scripts/.
# Cundamanix Static Analysis 

Quick notes and how-to for running the project locally with Docker.

## Prerequisites
- Docker 20.10+
- docker-compose (v2 recommended)

## Quick start (build & run)
1) Build the image and start the service:
   ```bash
   docker compose build --no-cache
   docker compose up --build -d
   ```

2) Open the app in your browser:
   - http://localhost:5001
   - Default credentials printed in logs: mobsf / mobsf

## Development vs Production
- The Docker image copies the project into `/app/src` at build time.
- For development, `docker-compose.yaml` mounts local `./src` into the container:
  ```yaml
  volumes:
    - ./src:/app/src
  ```
- Be aware: mounting `./src` overwrites `/app/src` inside the container. If your host `./src` is missing files, those files will be missing in the container too (this was causing `scripts/clean.sh` to be missing in some setups).

## Cleaning / Resetting DB & uploads
- The container does not run `scripts/clean.sh` by default.
- Run the clean script one time with the env var:
  ```bash
  docker compose run --rm -e RUN_CLEAN=true mobsf
  ```
- The clean script deletes the scan DB and uploaded/generated files — use with caution.

## Java / JDK
- MobSF needs a Java 8+ runtime to run some analysis features.
- The Dockerfile should install OpenJDK 11 and set `JAVA_HOME`.
- If you see `JDK 8+ is not available`, ensure that:
  - The image installs openjdk (Dockerfile), or
  - `JAVA_HOME` is set to the Java installation dir and `java` is in PATH.

## Debugging & troubleshooting
- Check service logs:
  ```bash
  docker compose logs -f mobsf
  ```
- Check that scripts and files are present:
  ```bash
  docker compose run --rm --entrypoint sh mobsf -c 'ls -la /app/src/scripts && [ -f /app/src/scripts/clean.sh ] && echo "clean.sh exists" || echo "clean.sh missing"'
  ```
- Check processes and port binding:
  ```bash
  docker compose exec mobsf sh -c 'ps aux | grep gunicorn || true; ss -lntp | grep 5001 || true'
  ```
- Run the entrypoint manually to debug:
  ```bash
  docker compose run --rm --service-ports --entrypoint sh mobsf -c 'bash -x /app/src/scripts/entrypoint.sh'
  ```
- If the app prints the REST API key and exits with `JDK 8+ is not available`, the JDK isn't detected.

## Stopping & removing containers
- Stop:
  ```bash
  docker compose stop mobsf
  ```
- Stop and remove everything:
  ```bash
  docker compose down
  ```
- Force stop:
  ```bash
  docker compose kill mobsf
  ```

## Notes / common gotchas
- Make sure `docker-compose.yaml` maps the host `./src` to `/app/src` if you intend to use your local files in the container.
  ```yaml
  volumes:
    - ./src:/app/src
  ```
- If you don't want to use the host files (use the image content instead), remove the `volumes` entry from docker-compose.yaml.
- If the container keeps restarting, check logs to identify whether:
  - `scripts/clean.sh` exits due to missing files or requires input,
  - Gunicorn fails to start,
  - JDK not found.

# cundamanix-static-analysis

## Usage

1. Install dependencies:
	```bash
	cd src
	pip install -r requirements.txt
	# or
	poetry install
	```

2. Start the server (port 5001):
	```bash
	bash scripts/entrypoint.sh
	```

3. API endpoint for permission-only PDF:
	- POST to `http://localhost:5001/api/v1/permissions_pdf` with JSON `{ "hash": "<apk_or_ipa_hash>" }` and header `Authorization: <api_key>`
	- Response: PDF report

4. Default superuser:
	- Username: mobsf
	- Password: mobsf

For more details, see the source code and templates in `src/mobsf/templates/pdf/`.
# cundamanix-static-analysis

