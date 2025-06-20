# Frontend - Intelligent Payroll Processor

This directory contains the frontend for the Intelligent Payroll Processor application. It is a modern Single-Page Application (SPA) built with **React** and **Vite**, using **Material-UI** for components and styling.

---

## Architecture & State Management

The frontend is designed for a clean separation of concerns, with a responsive UI that reacts to changes in the application's state.

- **React Components:** The UI is built with functional React components, organized by feature (e.g., `dashboard`, `contract`, `payroll`).
- **Redux Toolkit:** State management is handled by Redux Toolkit. This provides a centralized "store" for all application data, ensuring a predictable and maintainable state that is shared across all components.
- **API Service:** All communication with the backend is handled by a dedicated API service layer built with `axios`. This service makes all the HTTP requests and dispatches the results to the Redux store.

---

## Key Components

- **`PayrollDashboard.jsx`**: The main landing page, which displays high-level KPIs and the full employee list.
- **`EmployeeList.jsx`**: A `DataGrid` component that displays all employees in a sortable, paginated table.
- **`ContractManagement.jsx`**: The page for uploading and processing individual employee contracts.
- **Redux Slices (`payrollSlice.js`, `employeeSlice.js`, etc.)**: These files define the logic for fetching and updating data related to their specific domain.

---

## Sample Data for Bulk Import

To help with the bulk import feature, a sample Excel file is provided.

- **Location:** `public/sample_employees.xlsx`
- This file can be downloaded directly from the "Quick Actions" panel on the dashboard. It contains all the required and optional headers for a successful import.

---

## How to Run

1.  **Prerequisites:**
    - Node.js and npm (or your preferred package manager)

2.  **Installation:**
    From this directory (`Final_Hackathon/frontend`), run:
    ```bash
    npm install
    ```

3.  **Running the Development Server:**
    ```bash
    npm run dev
    ```
    The application will open in your browser at `http://localhost:5173` (or the next available port) and will hot-reload when you make changes to the code.
