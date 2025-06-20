# Intelligent Payroll Processor

An advanced, AI-powered payroll processing application designed to automate and streamline payroll operations from contract to payslip.

**Team:**
- Divya bharathi S - *Project Lead*
- Gemini 1.5 Flash - *AI Assistant*

---

## High-Level Overview

This project is a full-stack web application that leverages an agentic AI backend to create a robust and intelligent payroll management system. The application is designed to take a typically manual, error-prone, and time-consuming task and transform it into a fast, accurate, and automated workflow.

The system's core functionality starts with an employment contract and ends with a generated payslip, with several automated validation, calculation, and document generation steps in between.

---

## Project Architecture

The application is built with a modern frontend and a powerful backend, communicating via a REST API. The backend features a multi-agent system that orchestrates the entire payroll workflow.

[View the full interactive workflow diagram here](https://www.mermaidchart.com/app/projects/bd8b13aa-cbc2-4120-9aab-e7434399f70a/diagrams/e92be77a-909b-4201-afcf-df436ce35c82/version/v0.1/edit)

---

## Key Features

- **Centralized Dashboard:** A high-level overview of the organization's payroll health with key performance indicators (KPIs).
- **Automated, Agent-driven Payroll Runs:** A single contract upload triggers the entire backend workflow, from parsing to payslip generation.
- **Intelligent Document Parsing:** A `ContractReaderAgent` uses a Large Language Model (LLM) to read and understand unstructured contract documents (`.pdf`, `.docx`, `.txt`).
- **Full Employee Lifecycle Management:**
  - View all employees in a comprehensive list.
  - Automatically create employee records from new contracts.
  - Bulk import employees via Excel or CSV files.
- **Automated Calculations & Document Generation:** Automatically calculates salary breakdowns and generates professional PDF payslips.

---

## Setup & Running the Application

To run this project, you will need to start both the backend server and the frontend development server.

### 1. Backend Setup

The backend is a Python application powered by FastAPI.

**Prerequisites:**
- Python 3.9+
- An `.env` file with your MongoDB connection string and other required environment variables. See `env.example` for the required fields.

**Instructions:**
1. Navigate to the backend directory:
   ```bash
   cd Final_Hackathon/backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```
The backend API will be available at `http://127.0.0.1:8000`.

### 2. Frontend Setup

The frontend is a React application built with Vite.

**Prerequisites:**
- Node.js and npm

**Instructions:**
1. Navigate to the frontend directory:
   ```bash
   cd Final_Hackathon/frontend
   ```
2. Install the necessary npm packages:
   ```bash
   npm install
   ```
3. Run the frontend development server:
   ```bash
   npm run dev
   ```
The application will be accessible in your browser at `http://localhost:5173` (or the next available port).