from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import json
import re
import os

from ..config import settings
from ..models.payroll import ComplianceStatus, AgentStatus
from ..workflows.state import PayrollState

class ComplianceMapperAgent:
    """Agent 3: RAG-enabled compliance mapping and validation"""
    
    def __init__(self):
        self.name = "compliance_mapper"
        self.description = "Maps salary deductions with up-to-date tax policies using RAG"
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_API_KEY
        )
        self.vector_store = None
        self._initialize_rag()
        
    def _initialize_rag(self):
        """Initialize RAG system with tax rules"""
        try:
            # Initialize vector store
            self.vector_store = Chroma(
                collection_name="tax_compliance_rules",
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            # Add sample tax rules if vector store is empty
            if self.vector_store._collection.count() == 0:
                self._add_sample_tax_rules()
                
        except Exception as e:
            print(f"Warning: RAG initialization failed: {e}")
            self.vector_store = None
    
    def _add_sample_tax_rules(self):
        """Add sample tax rules to the vector store"""
        sample_rules = [
            {
                "text": "Provident Fund (PF) contribution is mandatory for employees earning up to 15,000 per month. Employee contribution is 12% of basic salary, capped at 1,800 per month.",
                "metadata": {"rule_type": "PF", "region": "IN", "year": "2024"}
            },
            {
                "text": "Employee State Insurance (ESI) is applicable for employees earning up to 21,000 per month. Employee contribution is 0.75% of gross salary.",
                "metadata": {"rule_type": "ESI", "region": "IN", "year": "2024"}
            },
            {
                "text": "Income Tax slabs for FY 2024-25: 0-3L: 0%, 3L-6L: 5%, 6L-9L: 10%, 9L-12L: 15%, 12L-15L: 20%, 15L+: 30%",
                "metadata": {"rule_type": "Income_Tax", "region": "IN", "year": "2024"}
            },
            {
                "text": "House Rent Allowance (HRA) exemption is the minimum of: 1) Actual HRA received, 2) 50% of basic salary for metro cities, 3) Actual rent paid minus 10% of basic salary.",
                "metadata": {"rule_type": "HRA", "region": "IN", "year": "2024"}
            },
            {
                "text": "Leave Travel Allowance (LTA) exemption is available for domestic travel twice in a block of 4 years, subject to actual travel expenses.",
                "metadata": {"rule_type": "LTA", "region": "IN", "year": "2024"}
            },
            {
                "text": "Gratuity is calculated as (Basic Salary × 4.81 × Years of Service) / 26. Tax exemption up to 20L for gratuity received.",
                "metadata": {"rule_type": "Gratuity", "region": "IN", "year": "2024"}
            }
        ]
        
        texts = [rule["text"] for rule in sample_rules]
        metadatas = [rule["metadata"] for rule in sample_rules]
        
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        print("✅ Sample tax rules added to RAG system")
    
    async def execute(self, state: PayrollState) -> PayrollState:
        """Execute compliance mapping process"""
        try:
            # Update agent status
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 10, "Starting compliance validation...")
            
            if not state.salary_breakdown:
                raise ValueError("Salary breakdown not available for compliance validation")
            
            # Query RAG for relevant tax rules
            relevant_rules = self._query_tax_rules(state.salary_breakdown)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 40, "Tax rules retrieved")
            
            # Validate compliance
            compliance_status = self._validate_compliance(state.salary_breakdown, relevant_rules)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 80, "Compliance validation completed")
            
            # Update state with compliance data
            state.compliance_status = compliance_status
            state.update_agent_progress(self.name, AgentStatus.COMPLETED, 100, "Compliance mapping completed")
            
            return state
            
        except Exception as e:
            state.update_agent_progress(self.name, AgentStatus.FAILED, 0, f"Error: {str(e)}")
            state.error_message = f"Compliance mapping failed: {str(e)}"
            return state
    
    def _query_tax_rules(self, salary_breakdown) -> List[str]:
        """Query RAG system for relevant tax rules"""
        if not self.vector_store:
            return ["RAG system not available - using default rules"]
        
        # Create query based on salary components
        query = f"""
        Tax rules for salary breakdown:
        - Basic Salary: {salary_breakdown.salary_components.basic_salary}
        - HRA: {salary_breakdown.salary_components.hra}
        - LTA: {salary_breakdown.salary_components.lta}
        - Gross Salary: {salary_breakdown.gross_salary}
        - PF Deduction: {salary_breakdown.deduction_components.pf}
        - ESI Deduction: {salary_breakdown.deduction_components.esi}
        """
        
        # Search for relevant rules
        results = self.vector_store.similarity_search(query, k=5)
        return [doc.page_content for doc in results]
    
    def _validate_compliance(self, salary_breakdown, tax_rules: List[str]) -> ComplianceStatus:
        """Validate compliance using LLM and tax rules"""
        
        prompt = PromptTemplate(
            input_variables=["salary_breakdown", "tax_rules"],
            template="""
            Analyze the following salary breakdown against the tax rules and validate compliance.
            Return a JSON response with compliance validation. Provide detailed, structured issues if any are found.

            Salary Breakdown:
            {salary_breakdown}
            
            Tax Rules:
            {tax_rules}
            
            Return a JSON response with the following structure:
            {{
                "is_compliant": true/false,
                "compliance_issues": [
                    {{
                        "issue_type": "e.g., Minimum Wage",
                        "description": "A detailed description of the compliance issue.",
                        "severity": "e.g., High",
                        "recommendation": "A suggestion to fix the issue."
                    }}
                ],
                "tax_slabs_applied": {{
                    "income_tax_slab": "slab_details",
                    "pf_cap": "15000",
                    "esi_threshold": "21000"
                }},
                "exemptions_claimed": {{
                    "hra_exemption": 0.0,
                    "lta_exemption": 0.0,
                    "standard_deduction": 50000
                }},
                "corrections_suggested": ["suggestion1", "suggestion2"]
            }}
            
            If there are no compliance issues, return an empty list for "compliance_issues".
            """
        )
        
        response = self.llm.invoke(
            prompt.format(
                salary_breakdown=str(salary_breakdown.dict()),
                tax_rules="\n".join(tax_rules)
            )
        )
        
        # Parse JSON response
        json_data = self._parse_json_response(response.content)
        
        return ComplianceStatus(
            is_compliant=json_data.get("is_compliant", True),
            compliance_issues=[
                issue["description"] if isinstance(issue, dict) and "description" in issue else str(issue)
                for issue in json_data.get("compliance_issues", [])
            ],
            tax_slabs_applied=json_data.get("tax_slabs_applied", {}),
            exemptions_claimed=json_data.get("exemptions_claimed", {}),
            corrections_suggested=json_data.get("corrections_suggested", [])
        )
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        json_string = response.strip()
        
        # Remove markdown code blocks
        if json_string.startswith('```json'):
            json_string = json_string[len('```json'):]
        if json_string.endswith('```'):
            json_string = json_string[:-len('```')]
        json_string = json_string.strip()
        
        # Use regex to find JSON object
        json_match = re.search(r'(\{.*\})', json_string, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
        
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse JSON response: {e}")
            return {
                "is_compliant": True,
                "compliance_issues": [],
                "tax_slabs_applied": {},
                "exemptions_claimed": {},
                "corrections_suggested": []
            } 