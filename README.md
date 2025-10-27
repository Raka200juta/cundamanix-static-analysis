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

