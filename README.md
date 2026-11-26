# Smart Resume Analyzer
Flask prototype: PDF/DOCX parsing, checklist score, role-keyword matching, feedback, SQLite analysis history and Chart.js dashboard.

## Run
1. Python 3.10+
2. `python -m venv .venv`
3. Activate: Windows `.venv\\Scripts\\activate`; macOS/Linux `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python app.py`
6. Visit http://127.0.0.1:5000

Scoring is a simple heuristic (10 checks x 10 points). ATS percentage compares the detected keywords against a sample skill list for the chosen role. It is not an actual ATS or hiring predictor.

For public deployment, implement file size limits, deletion policies, HTTPS, secure secrets, malware scanning and privacy disclosures.
