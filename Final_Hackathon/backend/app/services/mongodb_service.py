from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from bson import ObjectId
from fastapi import HTTPException
import uuid
import pandas as pd

from ..config import settings
from ..models.payroll import (
    PayrollResponse, ContractData, SalaryBreakdown, 
    ComplianceStatus, AnomalyReport, GeneratedDocument,
    WorkflowStatus, AgentStatus
)
from ..workflows.state import PayrollState

class MongoDBService:
    """Service class for MongoDB operations"""
    
    def __init__(self):
        self.db = settings.mongo_db
        self.payroll_requests = self.db.payroll_requests
        self.employees = self.db.employees
        self.workflow_states = self.db.workflow_states
        self.contracts = self.db.contracts
        self.salary_breakdowns = self.db.salary_breakdowns
        self.compliance_records = self.db.compliance_records
        self.anomaly_reports = self.db.anomaly_reports
        self.generated_documents = self.db.generated_documents
    
    # Payroll Request Operations
    async def create_payroll_request(self, payroll_response: PayrollResponse) -> str:
        """Create a new payroll request"""
        try:
            result = await self.payroll_requests.insert_one(payroll_response.dict())
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Failed to create payroll request: {str(e)}")
    
    async def get_payroll_request(self, request_id: str) -> Optional[Dict]:
        """Get payroll request by ID"""
        try:
            return await self.payroll_requests.find_one({"request_id": request_id})
        except Exception as e:
            raise Exception(f"Failed to get payroll request: {str(e)}")
    
    async def update_payroll_request(self, request_id: str, update_data: Dict) -> bool:
        """Update payroll request"""
        try:
            update_data["updated_at"] = datetime.now()
            result = await self.payroll_requests.update_one(
                {"request_id": request_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to update payroll request: {str(e)}")
    
    # Workflow State Operations
    async def save_workflow_state(self, request_id: str, state: PayrollState) -> bool:
        """Save workflow state to MongoDB"""
        try:
            # Convert state to serializable format
            state_dict = self._serialize_state(state)
            
            workflow_doc = {
                "request_id": request_id,
                "state": state_dict,
                "updated_at": datetime.now()
            }
            
            # Use upsert to create or update
            result = await self.workflow_states.update_one(
                {"request_id": request_id},
                {"$set": workflow_doc},
                upsert=True
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to save workflow state: {str(e)}")
    
    def _serialize_state(self, state: PayrollState) -> dict:
        """Convert PayrollState to serializable dictionary"""
        state_dict = {}
        
        # Basic fields
        for field in ['employee_id', 'contract_file_path', 'processing_month', 'region', 
                     'current_agent', 'error_message', 'created_at', 'updated_at']:
            if hasattr(state, field):
                value = getattr(state, field)
                if value is not None:
                    state_dict[field] = value
        
        # Enum fields
        if hasattr(state, 'workflow_status') and state.workflow_status:
            state_dict['workflow_status'] = state.workflow_status.value
        
        # Numeric fields
        if hasattr(state, 'progress_percentage'):
            state_dict['progress_percentage'] = state.progress_percentage
        
        # Pydantic model fields - convert to dict
        if hasattr(state, 'contract_data') and state.contract_data:
            state_dict['contract_data'] = state.contract_data.dict()
        
        if hasattr(state, 'salary_breakdown') and state.salary_breakdown:
            state_dict['salary_breakdown'] = state.salary_breakdown.dict()
        
        if hasattr(state, 'compliance_status') and state.compliance_status:
            state_dict['compliance_status'] = state.compliance_status.dict()
        
        if hasattr(state, 'anomaly_report') and state.anomaly_report:
            state_dict['anomaly_report'] = state.anomaly_report.dict()
        
        # List fields
        if hasattr(state, 'generated_documents') and state.generated_documents:
            state_dict['generated_documents'] = [doc.dict() for doc in state.generated_documents]
        
        # Agent progress - convert to serializable format
        if hasattr(state, 'agent_progress') and state.agent_progress:
            agent_progress_dict = {}
            for agent_name, progress in state.agent_progress.items():
                agent_progress_dict[agent_name] = {
                    'agent_name': progress.agent_name,
                    'status': progress.status.value if progress.status else None,
                    'progress': progress.progress,
                    'message': progress.message,
                    'started_at': progress.started_at,
                    'completed_at': progress.completed_at
                }
            state_dict['agent_progress'] = agent_progress_dict
        
        return state_dict
    
    async def get_workflow_state(self, request_id: str) -> Optional[Dict]:
        """Get workflow state by request ID"""
        try:
            return await self.workflow_states.find_one({"request_id": request_id})
        except Exception as e:
            raise Exception(f"Failed to get workflow state: {str(e)}")
    
    async def update_workflow_state_with_data(self, request_id: str, update_data: Dict) -> bool:
        """Update workflow state with specific data"""
        try:
            result = await self.workflow_states.update_one(
                {"request_id": request_id},
                {"$set": {"state." + k: v for k, v in update_data.items()}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to update workflow state: {str(e)}")
    
    # Employee Operations
    async def create_employee(self, employee_data: Dict) -> str:
        """Create a new employee, ensuring email and phone are unique"""
        try:
            # Check for uniqueness
            if await self.db.employees.find_one({"email": employee_data["email"]}):
                raise HTTPException(status_code=409, detail=f"Employee with email '{employee_data['email']}' already exists.")
            if await self.db.employees.find_one({"phone": employee_data["phone"]}):
                raise HTTPException(status_code=409, detail=f"Employee with phone '{employee_data['phone']}' already exists.")

            try:
                # Add additional metadata
                employee_data['employee_id'] = str(uuid.uuid4())
                employee_data['created_at'] = datetime.now()
                employee_data['updated_at'] = datetime.now()
                employee_data['status'] = 'Active'  # Set default status

                # Insert into MongoDB
                result = await self.db.employees.insert_one(employee_data)
                return employee_data["employee_id"]
            
            except Exception as e:
                # For other unexpected errors, log them and return a generic error
                # In a real app, you would log 'e' here
                raise HTTPException(status_code=500, detail="Failed to create employee due to a server error.")
        
        except HTTPException:
            raise  # Re-raise HTTPException to be handled by FastAPI
    
    async def get_employee(self, employee_id: str) -> Optional[Dict]:
        """Find a single employee by their unique employee_id."""
        return await self.db.employees.find_one({"employee_id": employee_id})

    async def get_all_employees(self) -> List[Dict[str, Any]]:
        """Fetch all employee records from the database."""
        employees_cursor = self.db.employees.find({})
        employees = await employees_cursor.to_list(length=1000)  # Adjust length as needed
        for emp in employees:
            emp["_id"] = str(emp["_id"]) # Convert ObjectId to string for JSON serialization
        return employees

    async def update_employee(self, employee_id: str, employee_data: Dict[str, Any]) -> bool:
        """Update an employee's data."""
        try:
            # Filter out any keys with None values to avoid overwriting existing fields with nulls
            update_data = {
                k: v for k, v in employee_data.items() if v is not None
            }
            
            if not update_data:
                return False # No data to update

            update_data["updated_at"] = datetime.now()

            result = await self.db.employees.update_one(
                {"employee_id": employee_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            # Log the error for debugging
            print(f"Error updating employee {employee_id}: {e}")
            return False
    
    async def delete_employee(self, employee_id: str) -> bool:
        """Delete an employee record by their unique employee_id."""
        try:
            result = await self.db.employees.delete_one({"employee_id": employee_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting employee {employee_id}: {e}")
            return False
    
    # Contract Operations
    async def save_contract_data(self, request_id: str, contract_data: ContractData) -> bool:
        """Save parsed contract data"""
        try:
            contract_dict = {
                "request_id": request_id,
                "contract_data": contract_data.dict(),
                "created_at": datetime.now()
            }
            
            result = await self.contracts.update_one(
                {"request_id": request_id},
                {"$set": contract_dict},
                upsert=True
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to save contract data: {str(e)}")
    
    async def get_contract_data(self, request_id: str) -> Optional[Dict]:
        """Get contract data by request ID"""
        try:
            return await self.contracts.find_one({"request_id": request_id})
        except Exception as e:
            raise Exception(f"Failed to get contract data: {str(e)}")
    
    # Salary Breakdown Operations
    async def save_salary_breakdown(self, request_id: str, salary_breakdown: SalaryBreakdown) -> bool:
        """Save calculated salary breakdown"""
        try:
            breakdown_dict = {
                "request_id": request_id,
                "salary_breakdown": salary_breakdown.dict(),
                "created_at": datetime.now()
            }
            
            result = await self.salary_breakdowns.update_one(
                {"request_id": request_id},
                {"$set": breakdown_dict},
                upsert=True
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to save salary breakdown: {str(e)}")
    
    async def get_salary_breakdown(self, request_id: str) -> Optional[Dict]:
        """Get salary breakdown by request ID"""
        try:
            return await self.salary_breakdowns.find_one({"request_id": request_id})
        except Exception as e:
            raise Exception(f"Failed to get salary breakdown: {str(e)}")
    
    # Compliance Operations
    async def save_compliance_status(self, request_id: str, compliance_status: ComplianceStatus) -> bool:
        """Save compliance status"""
        try:
            compliance_dict = {
                "request_id": request_id,
                "compliance_status": compliance_status.dict(),
                "created_at": datetime.now()
            }
            
            result = await self.compliance_records.update_one(
                {"request_id": request_id},
                {"$set": compliance_dict},
                upsert=True
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to save compliance status: {str(e)}")
    
    async def get_compliance_status(self, request_id: str) -> Optional[Dict]:
        """Get compliance status by request ID"""
        try:
            return await self.compliance_records.find_one({"request_id": request_id})
        except Exception as e:
            raise Exception(f"Failed to get compliance status: {str(e)}")
    
    # Anomaly Report Operations
    async def save_anomaly_report(self, request_id: str, anomaly_report: AnomalyReport) -> bool:
        """Save anomaly report"""
        try:
            anomaly_dict = {
                "request_id": request_id,
                "anomaly_report": anomaly_report.dict(),
                "created_at": datetime.now()
            }
            
            result = await self.anomaly_reports.update_one(
                {"request_id": request_id},
                {"$set": anomaly_dict},
                upsert=True
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to save anomaly report: {str(e)}")
    
    async def get_anomaly_report(self, request_id: str) -> Optional[Dict]:
        """Get anomaly report by request ID"""
        try:
            return await self.anomaly_reports.find_one({"request_id": request_id})
        except Exception as e:
            raise Exception(f"Failed to get anomaly report: {str(e)}")
    
    # Generated Document Operations
    async def save_generated_document(self, request_id: str, document: GeneratedDocument) -> bool:
        """Save generated document metadata"""
        try:
            document_dict = {
                "request_id": request_id,
                "document": document.dict(),
                "created_at": datetime.now()
            }
            
            result = await self.generated_documents.insert_one(document_dict)
            return True
        except Exception as e:
            raise Exception(f"Failed to save generated document: {str(e)}")
    
    async def get_generated_documents(self, request_id: str) -> List[Dict]:
        """Get all generated documents for a request"""
        try:
            cursor = self.generated_documents.find({"request_id": request_id})
            return await cursor.to_list(length=100)
        except Exception as e:
            raise Exception(f"Failed to get generated documents: {str(e)}")
    
    # Analytics and Reporting
    async def get_payroll_analytics(self, employee_id: str = None, month: str = None) -> Dict:
        """Get payroll analytics"""
        try:
            pipeline = []
            
            if employee_id:
                pipeline.append({"$match": {"employee_id": employee_id}})
            
            if month:
                pipeline.append({"$match": {"processing_month": month}})
            
            pipeline.extend([
                {"$group": {
                    "_id": "$workflow_status",
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$salary_breakdown.gross_salary"}
                }},
                {"$sort": {"count": -1}}
            ])
            
            analytics = await self.payroll_requests.aggregate(pipeline).to_list(length=100)
            return {"analytics": analytics}
        except Exception as e:
            raise Exception(f"Failed to get payroll analytics: {str(e)}")
    
    # Utility Methods
    async def get_all_payroll_requests(self, limit: int = 50) -> List[Dict]:
        """Get all payroll requests with pagination"""
        try:
            cursor = self.payroll_requests.find().sort("created_at", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            raise Exception(f"Failed to get payroll requests: {str(e)}")
    
    async def delete_payroll_request(self, request_id: str) -> bool:
        """Delete payroll request and all related data"""
        try:
            # Delete from all collections
            await self.payroll_requests.delete_one({"request_id": request_id})
            await self.workflow_states.delete_one({"request_id": request_id})
            await self.contracts.delete_one({"request_id": request_id})
            await self.salary_breakdowns.delete_one({"request_id": request_id})
            await self.compliance_records.delete_one({"request_id": request_id})
            await self.anomaly_reports.delete_one({"request_id": request_id})
            await self.generated_documents.delete_many({"request_id": request_id})
            
            return True
        except Exception as e:
            raise Exception(f"Failed to delete payroll request: {str(e)}")

    async def create_employee_from_contract(self, contract_data: ContractData) -> str:
        """
        Creates a new employee record from contract data if they don't already exist.
        Checks for existence based on employee_id.
        """
        existing_employee = await self.get_employee(contract_data.employee_id)
        if existing_employee:
            print(f"Employee with ID {contract_data.employee_id} already exists. Skipping creation.")
            return existing_employee['employee_id']

        employee_data = {
            "employee_id": contract_data.employee_id,
            "name": contract_data.employee_name,
            "email": contract_data.employee_email,
            "phone": contract_data.employee_phone,
            "designation": contract_data.designation,
            "department": contract_data.department,
            "join_date": contract_data.join_date,
            "status": "active", # Default status
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Remove any None values, as MongoDB doesn't need them
        employee_data = {k: v for k, v in employee_data.items() if v is not None}

        await self.employees.insert_one(employee_data)
        print(f"Successfully created new employee: {contract_data.employee_id}")
        return contract_data.employee_id

    async def bulk_create_employees(self, employees: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates multiple employees from a list of dictionaries.
        Handles basic employee info and salary components.
        Skips duplicates based on email or employee_id.
        """
        created_count = 0
        skipped_count = 0
        errors = []

        salary_component_keys = [
            "basic_salary", "hra", "lta", "variable_pay", 
            "bonuses", "other_allowances"
        ]

        for emp_data in employees:
            try:
                # Check for existing employee by email or employee_id
                if 'email' in emp_data and await self.employees.find_one({"email": emp_data['email']}):
                    skipped_count += 1
                    continue
                if 'employee_id' in emp_data and await self.employees.find_one({"employee_id": emp_data['employee_id']}):
                    skipped_count += 1
                    continue
                
                # Prepare data for insertion
                insert_data = {
                    'employee_id': emp_data.get('employee_id', str(uuid.uuid4())),
                    'name': emp_data.get('name'),
                    'email': emp_data.get('email'),
                    'phone': emp_data.get('phone'),
                    'designation': emp_data.get('designation'),
                    'department': emp_data.get('department'),
                    'join_date': pd.to_datetime(emp_data.get('join_date')).to_pydatetime() if emp_data.get('join_date') and pd.notna(emp_data.get('join_date')) else None,
                    'status': 'active',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }

                # Prepare salary components
                salary_components = {}
                for key in salary_component_keys:
                    # Check for key existence and ensure value is not NaN
                    if key in emp_data and pd.notna(emp_data[key]):
                        try:
                            salary_components[key] = float(emp_data[key])
                        except (ValueError, TypeError):
                            # Skip if value cannot be converted to float
                            pass
                
                if salary_components:
                    insert_data['salary_components'] = salary_components
                
                # Remove keys with None values to avoid storing them
                insert_data = {k: v for k, v in insert_data.items() if v is not None}
                
                await self.employees.insert_one(insert_data)
                created_count += 1

            except Exception as e:
                errors.append({"employee": emp_data.get('name'), "error": str(e)})

        return {
            "created_count": created_count,
            "skipped_count": skipped_count,
            "errors": errors
        }

# Global instance
mongodb_service = MongoDBService() 