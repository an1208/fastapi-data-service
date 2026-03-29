# FastAPI CSV Data Analysis Service


![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A production-style REST API built with **FastAPI** that accepts CSV file uploads, processes them using **Pandas**, and returns structured JSON containing summary statistics, data quality metrics, and column-level insights.

Designed to mirror real-world data ingestion and analytics backend services — the same architectural pattern used in large-scale vehicle data platforms and software-defined mobility systems.

---

## What it does

Upload any CSV file to the `/analyse` endpoint and receive:

- **Shape** — row and column counts
- **Column-level info** — data type, null count, null percentage, unique value count for every column
- **Numeric statistics** — mean, median, standard deviation, min, max, Q25, Q75 for all numeric columns
- **Categorical statistics** — top 5 most frequent values for all string/text columns
- **Data quality report** — total nulls, complete rows, and overall completeness percentage

---

## Why this project

This project demonstrates three core data engineering skills directly relevant to backend ML/data roles:

| Skill | How it's demonstrated |
|---|---|
| REST API design | FastAPI endpoint that handles file upload, validation, and structured JSON response |
| Data pipeline development | Pandas-based processing — ingestion → cleaning → transformation → output |
| Backend reliability | Automated test suite with 5 tests covering happy path, error cases, and accuracy |
| CI/CD | GitHub Actions workflow runs all tests automatically on every push |

---

## Tech stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| FastAPI | Web framework and API routing |
| Uvicorn | ASGI server |
| Pandas | CSV parsing and statistical computation |
| Pytest | Automated testing |
| GitHub Actions | CI/CD — automated test runs on every push |

---

## Project structure

```
fastapi-data-service/
├── .github/
│   └── workflows/
│       └── test.yml          ← CI/CD: auto-runs tests on every push
├── main.py                   ← FastAPI application and all endpoints
├── test_main.py              ← 5 automated tests (pytest)
├── sample_data.csv           ← Example CSV with intentional nulls for testing
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Quickstart

**1. Clone and set up environment**

```bash
git clone https://github.com/YOUR_USERNAME/fastapi-data-service.git
cd fastapi-data-service
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. Run the server**

```bash
uvicorn main:app --reload
```

Server starts at `http://127.0.0.1:8000`

**3. Open the interactive docs**

```
http://127.0.0.1:8000/docs
```

FastAPI auto-generates a Swagger UI — upload `sample_data.csv` directly from the browser and see the full JSON response.

---

## API endpoints

### `GET /`
Health check — confirms the service is running.

**Response:**
```json
{
  "message": "CSV Analysis API is running",
  "usage": "POST a CSV file to /analyse to get statistics"
}
```

---

### `POST /analyse`
Upload a CSV file and receive full statistics.

**Request:** `multipart/form-data` with a `.csv` file

**Example using curl:**
```bash
curl -X POST "http://127.0.0.1:8000/analyse" \
     -F "file=@sample_data.csv"
```

**Example response:**
```json
{
  "filename": "sample_data.csv",
  "shape": {
    "rows": 12,
    "columns": 5
  },
  "columns": {
    "name": {
      "dtype": "object",
      "null_count": 1,
      "null_percent": 8.33,
      "unique_count": 9
    },
    "age": {
      "dtype": "float64",
      "null_count": 0,
      "null_percent": 0.0,
      "unique_count": 10
    },
    "salary": {
      "dtype": "float64",
      "null_count": 1,
      "null_percent": 8.33,
      "unique_count": 11
    }
  },
  "numeric_statistics": {
    "age": {
      "mean": 34.5,
      "median": 32.0,
      "std": 7.84,
      "min": 26.0,
      "max": 52.0,
      "q25": 28.75,
      "q75": 40.5
    },
    "salary": {
      "mean": 76636.36,
      "median": 77000.0,
      "std": 14821.3,
      "min": 55000.0,
      "max": 102000.0,
      "q25": 64500.0,
      "q75": 86500.0
    }
  },
  "categorical_statistics": {
    "name": {
      "top_values": {
        "Alice": 2,
        "Bob": 1,
        "Carol": 1,
        "David": 1,
        "Eve": 1
      }
    }
  },
  "data_quality": {
    "total_nulls": 2,
    "complete_rows": 10,
    "completeness_percent": 83.33
  }
}
```

**Error responses:**

| Status | Condition |
|---|---|
| `400 Bad Request` | File is not a `.csv` |
| `422 Unprocessable Entity` | File could not be parsed as valid CSV |

---

## Running the tests

```bash
pytest test_main.py -v
```

**Expected output:**
```
test_main.py::test_root_endpoint               PASSED
test_main.py::test_analyse_valid_csv           PASSED
test_main.py::test_reject_non_csv              PASSED
test_main.py::test_null_detection              PASSED
test_main.py::test_numeric_statistics_accuracy PASSED

5 passed in 0.43s
```

**Test coverage check:**
```bash
pytest test_main.py --cov=main --cov-report=term-missing
```

---

## CI/CD pipeline

Every push to `main` automatically:

1. Spins up a fresh Ubuntu VM on GitHub's cloud infrastructure
2. Installs Python 3.11 and all dependencies (with pip caching for speed)
3. Runs the full test suite
4. Reports pass/fail status on the commit

Workflow file: `.github/workflows/test.yml`

If any test fails, the badge turns red and the push is flagged — preventing broken code from reaching the main branch.

---

## Limitations and next steps

**Current limitations:**
- Runs in memory — large files (>100MB) would need chunked streaming with `pd.read_csv(chunksize=...)`
- No authentication — a production version would require API keys or OAuth
- Single-file analysis only — a real data platform would handle batch jobs across thousands of files

**Natural extensions:**
- Add a `POST /compare` endpoint that accepts two CSVs and returns a diff of their statistics
- Persist results to a database (PostgreSQL) instead of returning in-response
- Add Docker containerisation so the service runs identically in any environment
- Deploy to AWS EC2 or a cloud platform and expose a public URL

---

## Author

**Anushka Sharma**
ECE undergraduate · ML/Data Analysis minor · Maharaja Surajmal Institute of Technology
[LinkedIn](https://www.linkedin.com/in/anushka-sharma-1208ans) · anushka.sh0812@gmail.com
