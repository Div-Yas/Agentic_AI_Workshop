from typing import Dict, List, Optional, Any
from datetime import datetime
from ..models.payroll import (
    WorkflowStatus, AgentStatus, ContractData, SalaryBreakdown,
    ComplianceStatus, AnomalyReport, GeneratedDocument, AgentProgress
)

class PayrollState:
    """State class for LangGraph payroll workflow"""
    
    def __init__(self):
        # Input data
        self.request_id: str = ""
        self.employee_id: str = ""
        self.contract_file_path: str = ""
        self.processing_month: str = ""
        self.region: str = "IN"
        
        # Agent outputs
        self.contract_data: Optional[ContractData] = None
        self.salary_breakdown: Optional[SalaryBreakdown] = None
        self.compliance_status: Optional[ComplianceStatus] = None
        self.anomaly_report: Optional[AnomalyReport] = None
        self.generated_documents: List[GeneratedDocument] = []
        
        # Workflow control
        self.current_agent: str = ""
        self.workflow_status: WorkflowStatus = WorkflowStatus.PENDING
        self.progress_percentage: int = 0
        self.error_message: Optional[str] = None
        
        # Agent progress tracking
        self.agent_progress: Dict[str, AgentProgress] = {}
        
        # Metadata
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for LangGraph"""
        return {
            "employee_id": self.employee_id,
            "contract_file_path": self.contract_file_path,
            "processing_month": self.processing_month,
            "region": self.region,
            "contract_data": self.contract_data.dict() if self.contract_data else None,
            "salary_breakdown": self.salary_breakdown.dict() if self.salary_breakdown else None,
            "compliance_status": self.compliance_status.dict() if self.compliance_status else None,
            "anomaly_report": self.anomaly_report.dict() if self.anomaly_report else None,
            "generated_documents": [doc.dict() for doc in self.generated_documents],
            "current_agent": self.current_agent,
            "workflow_status": self.workflow_status.value,
            "progress_percentage": self.progress_percentage,
            "error_message": self.error_message,
            "agent_progress": {name: progress.dict() for name, progress in self.agent_progress.items()},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PayrollState':
        """Create state from dictionary"""
        state = cls()
        state.employee_id = data.get("employee_id", "")
        state.contract_file_path = data.get("contract_file_path", "")
        state.processing_month = data.get("processing_month", "")
        state.region = data.get("region", "IN")
        
        # Reconstruct complex objects
        if data.get("contract_data"):
            state.contract_data = ContractData(**data["contract_data"])
        if data.get("salary_breakdown"):
            state.salary_breakdown = SalaryBreakdown(**data["salary_breakdown"])
        if data.get("compliance_status"):
            state.compliance_status = ComplianceStatus(**data["compliance_status"])
        if data.get("anomaly_report"):
            state.anomaly_report = AnomalyReport(**data["anomaly_report"])
        
        state.generated_documents = [
            GeneratedDocument(**doc) for doc in data.get("generated_documents", [])
        ]
        
        state.current_agent = data.get("current_agent", "")
        state.workflow_status = WorkflowStatus(data.get("workflow_status", "pending"))
        state.progress_percentage = data.get("progress_percentage", 0)
        state.error_message = data.get("error_message")
        
        # Reconstruct agent progress
        for name, progress_data in data.get("agent_progress", {}).items():
            state.agent_progress[name] = AgentProgress(**progress_data)
        
        return state
    
    def update_agent_progress(self, agent_name: str, status: AgentStatus, progress: int = 0, message: str = ""):
        """Update agent progress"""
        if agent_name not in self.agent_progress:
            self.agent_progress[agent_name] = AgentProgress(
                agent_name=agent_name,
                status=status,
                progress=progress,
                message=message,
                started_at=datetime.now() if status == AgentStatus.RUNNING else None
            )
        else:
            self.agent_progress[agent_name].status = status
            self.agent_progress[agent_name].progress = progress
            self.agent_progress[agent_name].message = message
            if status == AgentStatus.COMPLETED:
                self.agent_progress[agent_name].completed_at = datetime.now()
        
        self.updated_at = datetime.now()
    
    def calculate_overall_progress(self) -> int:
        """Calculate overall workflow progress"""
        if not self.agent_progress:
            return 0
        
        total_progress = sum(progress.progress for progress in self.agent_progress.values())
        return total_progress // len(self.agent_progress)
    
    def get_next_agent(self) -> Optional[str]:
        """Get the next agent to run based on current state"""
        agents = ["contract_reader", "salary_calculator", "compliance_mapper", "anomaly_detector", "document_generator"]
        
        for agent in agents:
            if agent not in self.agent_progress:
                return agent
            elif self.agent_progress[agent].status == AgentStatus.FAILED:
                return agent  # Retry failed agent
        
        return None
    
    def is_workflow_complete(self) -> bool:
        """Check if workflow is complete"""
        return all(
            progress.status == AgentStatus.COMPLETED 
            for progress in self.agent_progress.values()
        )
    
    def has_critical_errors(self) -> bool:
        """Check if there are critical errors that should stop the workflow"""
        return (
            self.workflow_status == WorkflowStatus.FAILED or
            any(
                progress.status == AgentStatus.FAILED and agent in ["contract_reader", "salary_calculator"]
                for agent, progress in self.agent_progress.items()
            )
        ) 