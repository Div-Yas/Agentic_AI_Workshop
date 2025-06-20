# Backend - Intelligent Payroll Processor

This directory contains the backend for the Intelligent Payroll Processor application. It is a Python-based API built with **FastAPI** that powers the agentic workflow and all business logic.

---

## Agentic Workflow

The core of the backend is a multi-agent system that processes payroll in a sequential, stateful workflow. When the `/api/v1/payroll/upload-and-process` endpoint is called, it triggers the following chain of agents:

1.  **`ContractReaderAgent`**: Parses the uploaded contract file (`.pdf`, `.docx`, `.txt`) using an LLM to extract key details. It also automatically creates a new employee record in the database.
2.  **`SalaryCalculatorAgent`**: Calculates the detailed salary breakdown, including all earnings and deductions.
3.  **`ComplianceMapperAgent`**: Checks the salary breakdown against regional compliance rules.
4.  **`AnomalyDetectorAgent`**: Analyzes the data for any unusual or suspicious entries.
5.  **`DocumentGeneratorAgent`**: Creates the final PDF payslip.

---

## API Endpoints

All endpoints are available under the `/api/v1` prefix.

### Payroll & Contract Processing
- `POST /payroll/upload-and-process`: The main endpoint to trigger the full payroll workflow by uploading a contract file.
- `GET /downloads/{filename}`: Downloads a generated document (e.g., payslip).

### Employee Management
- `GET /employees`: Retrieves a list of all employees.
- `POST /employees/import`: Bulk-imports employees from an Excel or CSV file. The file must contain the headers specified in the sample file available on the frontend.

### Dashboard
- `GET /dashboard/summary`: Fetches the KPIs and data needed for the main dashboard.

---

## How to Run

1.  **Prerequisites:**
    - Python 3.9+
    - An active virtual environment.
    - An `.env` file with your `MONGODB_URI` and any other required keys (see `env.example`).

2.  **Installation:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Running the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be live at `http://127.0.0.1:8000` and will automatically reload on code changes. 