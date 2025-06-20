from .contract_reader import ContractReaderAgent
from .salary_calculator import SalaryCalculatorAgent
from .compliance_mapper import ComplianceMapperAgent
from .anomaly_detector import AnomalyDetectorAgent
from .document_generator import DocumentGeneratorAgent

# Agent Registry
AGENT_REGISTRY = {
    "contract_reader": ContractReaderAgent,
    "salary_calculator": SalaryCalculatorAgent,
    "compliance_mapper": ComplianceMapperAgent,
    "anomaly_detector": AnomalyDetectorAgent,
    "document_generator": DocumentGeneratorAgent,
}

def get_agent(agent_name: str):
    """Get agent instance by name"""
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Agent '{agent_name}' not found. Available agents: {list(AGENT_REGISTRY.keys())}")
    
    return AGENT_REGISTRY[agent_name]()

def list_agents() -> list:
    """List all available agents"""
    return list(AGENT_REGISTRY.keys()) 