#!/usr/bin/env python3
"""
Test script for MongoDB integration
Demonstrates creating sample data and testing API endpoints
"""

import asyncio
import json
from datetime import datetime
import uuid

# Import the MongoDB service
from app.services.mongodb_service import mongodb_service
from app.models.payroll import (
    PayrollRequest, PayrollResponse, ContractData, SalaryComponent,
    WorkflowStatus, AgentStatus
)
from app.workflows.state import PayrollState

async def test_mongodb_integration():
    """Test MongoDB integration with sample data"""
    
    print("🚀 Testing MongoDB Integration")
    print("=" * 50)
    
    try:
        # Test 1: Create a sample employee
        print("\n1. Creating sample employee...")
        employee_data = {
            "employee_id": "EMP001",
            "name": "John Doe",
            "email": "john.doe@company.com",
            "phone": "+91-9876543210",
            "department": "Engineering",
            "designation": "Senior Software Engineer",
            "join_date": "2023-01-15"
        }
        
        employee_id = await mongodb_service.create_employee(employee_data)
        print(f"✅ Employee created with ID: {employee_id}")
        
        # Test 2: Create a sample payroll request
        print("\n2. Creating sample payroll request...")
        payroll_request = PayrollRequest(
            employee_id="EMP001",
            contract_file_path="sample_contract.txt",
            processing_month="2024-01",
            region="IN"
        )
        
        payroll_response = PayrollResponse(
            request_id=str(uuid.uuid4()),
            employee_id=payroll_request.employee_id,
            workflow_status=WorkflowStatus.PENDING,
            progress_percentage=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        request_id = await mongodb_service.create_payroll_request(payroll_response)
        print(f"✅ Payroll request created with ID: {request_id}")
        
        # Test 3: Create sample contract data
        print("\n3. Creating sample contract data...")
        contract_data = ContractData(
            employee_id="EMP001",
            employee_name="John Doe",
            designation="Senior Software Engineer",
            department="Engineering",
            join_date=datetime(2023, 1, 15),
            salary_components=SalaryComponent(
                basic_salary=80000.0,
                hra=32000.0,
                lta=8000.0,
                variable_pay=20000.0,
                bonuses=0.0,
                other_allowances=5000.0
            ),
            statutory_obligations=["PF", "ESI", "Gratuity"],
            region="IN",
            currency="INR"
        )
        
        await mongodb_service.save_contract_data(payroll_response.request_id, contract_data)
        print("✅ Contract data saved")
        
        # Test 4: Create workflow state
        print("\n4. Creating workflow state...")
        workflow_state = PayrollState()
        workflow_state.employee_id = "EMP001"
        workflow_state.contract_file_path = "sample_contract.txt"
        workflow_state.processing_month = "2024-01"
        workflow_state.region = "IN"
        workflow_state.contract_data = contract_data
        workflow_state.current_agent = "contract_reader"
        workflow_state.workflow_status = WorkflowStatus.PROCESSING
        workflow_state.progress_percentage = 20
        
        await mongodb_service.save_workflow_state(payroll_response.request_id, workflow_state)
        print("✅ Workflow state saved")
        
        # Test 5: Retrieve and display data
        print("\n5. Retrieving saved data...")
        
        # Get employee
        employee = await mongodb_service.get_employee("EMP001")
        print(f"✅ Employee retrieved: {employee['name']} - {employee['designation']}")
        
        # Get payroll request
        payroll_req = await mongodb_service.get_payroll_request(payroll_response.request_id)
        print(f"✅ Payroll request retrieved: Status - {payroll_req['workflow_status']}")
        
        # Get contract data
        contract = await mongodb_service.get_contract_data(payroll_response.request_id)
        print(f"✅ Contract data retrieved: Basic Salary - ₹{contract['contract_data']['salary_components']['basic_salary']}")
        
        # Get workflow state
        workflow = await mongodb_service.get_workflow_state(payroll_response.request_id)
        print(f"✅ Workflow state retrieved: Progress - {workflow['state']['progress_percentage']}%")
        
        # Test 6: Analytics
        print("\n6. Testing analytics...")
        analytics = await mongodb_service.get_payroll_analytics()
        print(f"✅ Analytics retrieved: {len(analytics['analytics'])} records")
        
        print("\n" + "=" * 50)
        print("🎉 All MongoDB tests passed successfully!")
        print("\nNext steps:")
        print("1. Start the FastAPI server: python3 -m uvicorn app.main:app --reload")
        print("2. Test API endpoints at: http://localhost:8000/docs")
        print("3. Use the sample data created in this test")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

async def test_api_endpoints():
    """Test the FastAPI endpoints"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    # This would require the FastAPI server to be running
    # For now, just show the expected endpoints
    print("\nAvailable API endpoints:")
    print("- POST /api/v1/payroll/process - Process payroll")
    print("- GET /api/v1/payroll/{request_id} - Get payroll status")
    print("- GET /api/v1/payroll/employee/{employee_id} - Get employee payroll history")
    print("- POST /api/v1/employees - Create employee")
    print("- GET /api/v1/employees/{employee_id} - Get employee details")
    print("- PUT /api/v1/employees/{employee_id} - Update employee")
    print("- GET /api/v1/workflow/{request_id} - Get workflow state")
    print("- PUT /api/v1/workflow/{request_id} - Update workflow state")
    print("- GET /api/v1/health - Health check")
    print("- GET /api/v1/agents - List agents")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_mongodb_integration())
    asyncio.run(test_api_endpoints()) 