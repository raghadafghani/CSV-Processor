# CSV Processor

[![Build, Test & Deploy](https://github.com/USERNAME/REPOSITORY/actions/workflows/build-test-deploy.yml/badge.svg)](https://github.com/USERNAME/REPOSITORY/actions/workflows/build-test-deploy.yml)
[![Docker Image](https://ghcr-badge.egpl.dev/USERNAME/REPOSITORY/latest_tag?trim=major&label=Docker%20Image)](https://github.com/USERNAME/REPOSITORY/pkgs/container/REPOSITORY)
[![Security Scan](https://github.com/USERNAME/REPOSITORY/actions/workflows/build-test-deploy.yml/badge.svg?event=push)](https://github.com/USERNAME/REPOSITORY/actions/workflows/build-test-deploy.yml)

A clean, Apple-designed web application for processing CSV files. Built with Python FastAPI and a minimalist interface.

## Features

- **View All**: Display all rows from CSV files
- **Filter**: Filter rows based on column values
- **Transform**: Transform column values (uppercase, lowercase, trim)
- **Aggregate**: Count occurrences by column values
- **Sort**: Sort rows by column values
- **Download**: Download processed CSV files

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the application:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

4. Open your browser and navigate to:
```
http://localhost:8000
```

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root (see `.env.example` for reference):

- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DEBUG`: Enable debug mode (default: `False`)
- `CORS_ORIGINS`: Comma-separated list of allowed origins, or `*` for all (default: `*`)
- `STATIC_DIR`: Directory for static files (default: `static`)

## Testing

Run unit tests using pytest:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

The test suite includes:
- **CSV Processing Functions**: 10+ unit tests for core processing logic
- **API Endpoints**: 15+ integration tests for all endpoints
- **Error Handling**: Tests for edge cases and error scenarios

## Graceful Shutdown

The application handles graceful shutdown on SIGINT (Ctrl+C) and SIGTERM signals. When a shutdown signal is received, the server will:
1. Stop accepting new requests
2. Complete processing of current requests
3. Clean up resources
4. Exit gracefully

## Usage

1. **Upload CSV**: Drag and drop or click to select a CSV file
2. **Choose Operation**: Select the processing operation you want
3. **Configure Options**: Enter the required parameters for your operation
4. **Process**: Click "Process CSV" to process your file
5. **Download**: Download the processed CSV file

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### CSV Processing
- `POST /api/process/csv` - Process CSV files
  - Parameters: `file`, `operation`, `filter_column`, `filter_value`, `transform_column`, `transform_operation`

### Download
- `POST /api/download/csv` - Download processed CSV data

## Project Structure

```
SigmaProject/
├── main.py              # FastAPI backend
├── test_main.py         # Unit tests
├── requirements.txt     # Python dependencies
├── pytest.ini          # Pytest configuration
├── .env.example         # Environment variables example
├── README.md           # This file
└── static/             # Frontend files
    ├── index.html      # Main HTML page
    ├── style.css       # Apple-style CSS
    └── script.js       # Frontend logic
```

## Technologies

- **Backend**: Python 3.8+, FastAPI
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Server**: Uvicorn

## CI/CD Pipeline

This project uses GitHub Actions for automated build, test, and deployment. The pipeline includes:

- **🚀 Checkout & Setup**: Code checkout and Python environment setup
- **🧪 Test**: Unit tests with coverage reporting
- **🏗️ Build**: Docker image creation with multi-platform support
- **🔒 Security Scan**: Vulnerability scanning with Trivy and pip-audit
- **📦 Push to Registry**: Image push to GitHub Container Registry
- **☸️ Deploy to EKS**: Automated Kubernetes deployment

### Required Secrets

Configure these secrets in your GitHub repository settings:

```
AWS_ACCESS_KEY_ID       # AWS IAM user access key
AWS_SECRET_ACCESS_KEY   # AWS IAM user secret key
AWS_REGION             # AWS region (e.g., us-west-2)
EKS_CLUSTER_NAME       # Name of your EKS cluster
```

### Docker Image

The application is automatically built and pushed to GitHub Container Registry:

```bash
# Pull the latest image
docker pull ghcr.io/USERNAME/REPOSITORY:latest

# Run locally
docker run -p 8000:8000 ghcr.io/USERNAME/REPOSITORY:latest
```

## License

MIT License
