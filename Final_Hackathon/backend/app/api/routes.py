from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid
import json
import os
import pandas as pd
import io
from bson import ObjectId
import traceback

from ..config import settings
from ..models.payroll import (
    PayrollRequest, PayrollResponse, ContractData, 
    SalaryBreakdown, ComplianceStatus, AnomalyReport,
    WorkflowStatus, AgentStatus
)
from ..workflows.state import PayrollState
from ..services.mongodb_service import mongodb_service
from ..workflows.workflow import run_workflow

router = APIRouter()

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, list):
        return [json_serial(i) for i in obj]
    if isinstance(obj, dict):
        return {k: json_serial(v) for k, v in obj.items()}
    return obj

@router.post("/payroll/process", response_model=PayrollResponse)
async def process_payroll(
    request: PayrollRequest,
    background_tasks: BackgroundTasks
):
    """Process payroll for an employee"""
    try:
        request_id = str(uuid.uuid4())
        
        payroll_response = PayrollResponse(
            request_id=request_id,
            employee_id=request.employee_id,
            workflow_status=WorkflowStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await mongodb_service.create_payroll_request(payroll_response)
        
        workflow_state = PayrollState()
        workflow_state.employee_id = request.employee_id
        workflow_state.contract_file_path = request.contract_file_path
        workflow_state.processing_month = request.processing_month
        workflow_state.region = request.region
        
        await mongodb_service.save_workflow_state(request_id, workflow_state)
        
        return payroll_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payroll: {str(e)}")

@router.get("/payroll/{request_id}", response_model=PayrollResponse)
async def get_payroll_status(request_id: str):
    """Get payroll processing status"""
    try:
        payroll_data = await mongodb_service.get_payroll_request(request_id)
        if not payroll_data:
            raise HTTPException(status_code=404, detail="Payroll request not found")
        
        payroll_data.pop("_id", None)
        return PayrollResponse(**payroll_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payroll status: {str(e)}")

@router.post("/payroll/upload-and-process", response_model=Dict[str, Any])
async def upload_and_process_contract(file: UploadFile = File(...)):
    """
    Accepts a contract file, processes it, and returns the full payroll details.
    """
    if not file.content_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    request_id = str(uuid.uuid4())
    
    # Save the uploaded file with just the filename
    filename = f"{request_id}_{file.filename}"
    file_location = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Create initial state with just the filename
    initial_state = PayrollState()
    initial_state.request_id = request_id
    initial_state.contract_file_path = filename  # Just the filename, not full path
    initial_state.processing_month = date.today().strftime("%Y-%m")

    try:
        # Run the workflow
        final_state = await run_workflow(initial_state)

        if final_state.error_message:
            print("WORKFLOW ERROR:", final_state.error_message)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=final_state.error_message)

        # Construct response
        payslip_doc = next((doc for doc in final_state.generated_documents if doc.document_type == 'payslip'), None)
        
        response = {
            "request_id": final_state.request_id,
            "contract_data": final_state.contract_data.dict() if final_state.contract_data else {},
            "salary_breakdown": final_state.salary_breakdown.dict() if final_state.salary_breakdown else {},
            "compliance_flags": final_state.compliance_status.compliance_issues if final_state.compliance_status else [],
            "payslip_url": f"/api/v1/downloads/{payslip_doc.file_name}" if payslip_doc else None
        }
        
        return response
        
    except Exception as e:
        print("UPLOAD ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process payroll: {str(e)}")

@router.get("/payroll/employee/{employee_id}", response_model=List[PayrollResponse])
async def get_employee_payroll_history(employee_id: str):
    """Get payroll history for an employee"""
    try:
        # Get from MongoDB
        cursor = payroll_requests_collection.find({"employee_id": employee_id})
        payroll_history = await cursor.to_list(length=100)
        
        # Convert MongoDB documents to PayrollResponse objects
        responses = []
        for doc in payroll_history:
            doc.pop("_id", None)  # Remove MongoDB _id
            responses.append(PayrollResponse(**doc))
        
        return responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payroll history: {str(e)}")

@router.post("/employees", response_model=Dict[str, Any])
async def create_employee(employee_data: Dict[str, Any]):
    """Create a new employee record with unique email and phone validation."""
    try:
        employee_id = await mongodb_service.create_employee(employee_data)
        return {
            "success": True,
            "employee_id": employee_id,
            "message": "Employee created successfully"
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions from the service layer
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/employees", response_model=List[Dict[str, Any]])
async def list_employees():
    """List all employees."""
    try:
        employees = await mongodb_service.get_all_employees()
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list employees: {str(e)}")

@router.get("/employees/{employee_id}", response_model=Dict[str, Any])
async def get_employee(employee_id: str):
    """Get employee details by their unique ID."""
    try:
        employee = await mongodb_service.get_employee(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee.pop("_id", None)  # Remove MongoDB's internal ID
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get employee: {str(e)}")

@router.put("/employees/{employee_id}", response_model=Dict[str, Any])
async def update_employee(employee_id: str, employee_data: Dict[str, Any]):
    """Update employee details."""
    try:
        # Here you could add logic to prevent updating unique fields to duplicate values
        # For now, we'll just update the other fields.
        success = await mongodb_service.update_employee(employee_id, employee_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Employee not found or no changes made")
        
        return {
            "success": True,
            "message": "Employee updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update employee: {str(e)}")

@router.delete("/employees/{employee_id}", response_model=Dict[str, Any])
async def delete_employee_record(employee_id: str):
    """Delete an employee record."""
    try:
        success = await mongodb_service.delete_employee(employee_id)
        if not success:
            raise HTTPException(status_code=404, detail="Employee not found or could not be deleted")
        
        return {
            "success": True,
            "message": "Employee deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete employee: {str(e)}")

@router.post("/employees/import", response_model=Dict[str, Any])
async def import_employees(file: UploadFile = File(...)):
    """
    Imports employees from an Excel or CSV file.
    The file must contain columns for basic employee info, and can optionally include salary components.
    
    Required columns:
    - employee_id
    - name
    - email
    
    Optional columns:
    - phone
    - designation
    - department
    - join_date
    - basic_salary
    - hra
    - lta
    - variable_pay
    - bonuses
    - other_allowances
    """
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel (.xlsx) or CSV (.csv) file.")

    try:
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(content))
            
        # Basic validation for required columns
        required_columns = {'employee_id', 'name', 'email'}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")
            
        # Convert to list of dictionaries
        employees_to_create = df.to_dict(orient='records')
        
        # Call the service to handle bulk creation
        result = await mongodb_service.bulk_create_employees(employees_to_create)
        
        return {
            "success": True,
            "message": "Employee import process completed.",
            "details": result
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"An error occurred: {str(e)}"},
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        await settings.mongo_db.command("ping")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/agents")
async def list_agents():
    """List available agents"""
    return {
        "agents": [
            {
                "name": "contract_reader",
                "description": "Parses employment contracts to extract salary components and benefits",
                "status": "available"
            },
            {
                "name": "salary_calculator", 
                "description": "Calculates salary breakdown and tax deductions",
                "status": "available"
            },
            {
                "name": "compliance_mapper",
                "description": "Maps salary deductions with up-to-date tax policies using RAG",
                "status": "available"
            },
            {
                "name": "anomaly_detector",
                "description": "Flags discrepancies in calculation and tax treatment",
                "status": "available"
            },
            {
                "name": "document_generator",
                "description": "Generates downloadable payslips and tax forms",
                "status": "available"
            }
        ]
    }

@router.get("/downloads/{filename}")
async def download_file(filename: str):
    """Download a file from the output directory."""
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """Get a summary of dashboard KPIs."""
    try:
        # 1. Total Employees
        total_employees = await mongodb_service.employees.count_documents({})

        # 2. Recent Payroll Runs
        payroll_runs_cursor = mongodb_service.payroll_requests.find({}).sort("created_at", -1).limit(5)
        recent_payroll_runs = await payroll_runs_cursor.to_list(length=5)

        # 3. Anomaly Alerts (High severity)
        anomalies_cursor = mongodb_service.anomaly_reports.find({"severity": "High"}).sort("detected_at", -1).limit(5)
        anomaly_alerts = await anomalies_cursor.to_list(length=5)
        
        # 4. Payroll Accuracy
        total_runs = await mongodb_service.payroll_requests.count_documents({})
        runs_with_high_anomalies = await mongodb_service.anomaly_reports.count_documents({"severity": "High"})
        
        if total_runs > 0:
            payroll_accuracy = ((total_runs - runs_with_high_anomalies) / total_runs) * 100
        else:
            payroll_accuracy = 0

        # 5. Compliance Status
        # Count runs that had compliance issues
        runs_with_compliance_issues = await mongodb_service.compliance_records.count_documents({
            "compliance_status.compliance_issues": {"$not": {"$size": 0}}
        })
        if total_runs > 0:
            compliance_status = ((total_runs - runs_with_compliance_issues) / total_runs) * 100
        else:
            compliance_status = 0

        # 6. Total Disbursed
        # Aggregate the net_salary from all saved salary breakdowns
        all_breakdowns_cursor = mongodb_service.salary_breakdowns.find({})
        all_breakdowns = await all_breakdowns_cursor.to_list(length=None) # Use with caution on very large datasets
        total_disbursed = sum(item.get('salary_breakdown', {}).get('net_salary', 0) for item in all_breakdowns)

        summary_data = {
            "kpis": {
                "total_employees": total_employees,
                "payroll_accuracy": round(payroll_accuracy, 2),
                "compliance_status": round(compliance_status, 2),
                "total_disbursed": total_disbursed
            },
            "recent_payroll_runs": recent_payroll_runs,
            "anomaly_alerts": anomaly_alerts
        }

        # Use the custom JSON serializer
        return JSONResponse(content=json_serial(summary_data))
        
    except Exception as e:
        print(f"Error in /dashboard/summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}") 