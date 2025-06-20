from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentStatus(str, Enum):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SalaryComponent(BaseModel):
    basic_salary: float
    hra: Optional[float] = 0.0
    lta: Optional[float] = 0.0
    variable_pay: Optional[float] = 0.0
    bonuses: Optional[float] = 0.0
    other_allowances: Optional[float] = 0.0

class DeductionComponent(BaseModel):
    pf: Optional[float] = 0.0
    tds: Optional[float] = 0.0
    esi: Optional[float] = 0.0
    gratuity: Optional[float] = 0.0
    other_deductions: Optional[float] = 0.0

class ContractData(BaseModel):
    employee_id: str
    employee_name: str
    employee_email: Optional[str] = None
    employee_phone: Optional[str] = None
    designation: str
    department: str
    join_date: datetime
    salary_components: SalaryComponent
    statutory_obligations: List[str] = []
    region: str = "IN"
    currency: str = "INR"

class SalaryBreakdown(BaseModel):
    gross_salary: float
    net_salary: float
    total_earnings: float
    total_deductions: float
    salary_components: SalaryComponent
    deduction_components: DeductionComponent
    calculation_justification: Dict[str, str] = {}

class ComplianceStatus(BaseModel):
    is_compliant: bool
    compliance_issues: List[str] = []
    tax_slabs_applied: Dict[str, Any] = {}
    exemptions_claimed: Dict[str, float] = {}
    corrections_suggested: List[str] = []

class AnomalyReport(BaseModel):
    has_anomalies: bool
    anomalies: List[Dict[str, Any]] = []
    risk_level: str = "low"  # low, medium, high
    flags: List[str] = []

class GeneratedDocument(BaseModel):
    document_type: str  # payslip, form16, etc.
    file_path: str
    file_name: str
    generated_at: datetime
    download_url: Optional[str] = None

class PayrollRequest(BaseModel):
    employee_id: str
    contract_file_path: str
    processing_month: str
    region: str = "IN"

class PayrollResponse(BaseModel):
    request_id: str
    employee_id: str
    workflow_status: WorkflowStatus
    current_agent: Optional[str] = None
    progress_percentage: int = 0
    contract_data: Optional[ContractData] = None
    salary_breakdown: Optional[SalaryBreakdown] = None
    compliance_status: Optional[ComplianceStatus] = None
    anomaly_report: Optional[AnomalyReport] = None
    generated_documents: List[GeneratedDocument] = []
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class AgentProgress(BaseModel):
    agent_name: str
    status: AgentStatus
    progress: int = 0
    message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None 