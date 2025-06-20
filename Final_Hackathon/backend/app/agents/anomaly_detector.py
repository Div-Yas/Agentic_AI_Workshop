from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import json
import re
import statistics

from ..config import settings
from ..models.payroll import AnomalyReport, AgentStatus
from ..workflows.state import PayrollState

class AnomalyDetectorAgent:
    """Agent 4: Detects anomalies and flags discrepancies"""
    
    def __init__(self):
        self.name = "anomaly_detector"
        self.description = "Flags discrepancies in calculation and tax treatment"
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        
    async def execute(self, state: PayrollState) -> PayrollState:
        """Execute anomaly detection process"""
        try:
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 10, "Starting anomaly detection...")
            
            if not state.salary_breakdown:
                raise ValueError("Salary breakdown not available")
            
            # Detect anomalies
            anomalies = self._detect_anomalies(state.salary_breakdown, state.compliance_status)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 70, "Anomalies detected")
            
            # Create anomaly report
            anomaly_report = AnomalyReport(
                has_anomalies=len(anomalies) > 0,
                anomalies=anomalies,
                risk_level="low" if len(anomalies) == 0 else "medium",
                flags=[f"Anomaly: {a.get('description', 'Unknown')}" for a in anomalies]
            )
            
            state.anomaly_report = anomaly_report
            state.update_agent_progress(self.name, AgentStatus.COMPLETED, 100, "Anomaly detection completed")
            
            return state
            
        except Exception as e:
            state.update_agent_progress(self.name, AgentStatus.FAILED, 0, f"Error: {str(e)}")
            state.error_message = f"Anomaly detection failed: {str(e)}"
            return state
    
    def _detect_anomalies(self, salary_breakdown, compliance_status) -> List[Dict[str, Any]]:
        """Detect anomalies in salary breakdown"""
        anomalies = []
        
        # Check basic salary anomalies
        basic_salary = salary_breakdown.salary_components.basic_salary
        if basic_salary < 15000:
            anomalies.append({
                "type": "basic_salary",
                "severity": "high",
                "description": f"Basic salary ({basic_salary}) is below minimum wage"
            })
        
        # Check PF anomalies
        pf_amount = salary_breakdown.deduction_components.pf
        expected_pf = min(basic_salary * 0.12, 15000)
        if abs(pf_amount - expected_pf) > 1:
            anomalies.append({
                "type": "pf",
                "severity": "high",
                "description": f"PF amount ({pf_amount}) doesn't match expected ({expected_pf})"
            })
        
        return anomalies
    
    def _detect_statistical_anomalies(self, salary_breakdown) -> List[Dict[str, Any]]:
        """Detect statistical anomalies using mathematical analysis"""
        anomalies = []
        
        # Check for extreme values
        basic_salary = salary_breakdown.salary_components.basic_salary
        gross_salary = salary_breakdown.gross_salary
        
        # Anomaly: Basic salary too low (below minimum wage)
        if basic_salary < 15000:  # Assuming minimum wage
            anomalies.append({
                "type": "statistical",
                "category": "basic_salary",
                "severity": "high",
                "description": f"Basic salary ({basic_salary}) is below minimum wage threshold",
                "suggestion": "Review basic salary against minimum wage requirements"
            })
        
        # Anomaly: Basic salary too high (potential data entry error)
        if basic_salary > 500000:  # Unusually high basic salary
            anomalies.append({
                "type": "statistical",
                "category": "basic_salary",
                "severity": "medium",
                "description": f"Basic salary ({basic_salary}) is unusually high",
                "suggestion": "Verify basic salary amount for data entry accuracy"
            })
        
        # Anomaly: HRA exceeds 50% of basic salary
        hra = salary_breakdown.salary_components.hra
        if hra > (basic_salary * 0.5):
            anomalies.append({
                "type": "statistical",
                "category": "hra",
                "severity": "medium",
                "description": f"HRA ({hra}) exceeds 50% of basic salary ({basic_salary})",
                "suggestion": "Review HRA calculation and tax implications"
            })
        
        # Anomaly: Deductions exceed reasonable threshold
        total_deductions = salary_breakdown.total_deductions
        deduction_percentage = (total_deductions / gross_salary) * 100
        if deduction_percentage > 40:  # More than 40% deductions
            anomalies.append({
                "type": "statistical",
                "category": "deductions",
                "severity": "high",
                "description": f"Total deductions ({total_deductions}) are {deduction_percentage:.1f}% of gross salary",
                "suggestion": "Review deduction calculations and employee consent"
            })
        
        return anomalies
    
    def _detect_rule_anomalies(self, salary_breakdown, compliance_status) -> List[Dict[str, Any]]:
        """Detect rule-based anomalies"""
        anomalies = []
        
        # Check PF anomalies
        pf_amount = salary_breakdown.deduction_components.pf
        basic_salary = salary_breakdown.salary_components.basic_salary
        
        # PF should be 12% of basic salary, capped at 15,000
        expected_pf = min(basic_salary * 0.12, 15000)
        if abs(pf_amount - expected_pf) > 1:  # Allow for rounding differences
            anomalies.append({
                "type": "rule_based",
                "category": "pf",
                "severity": "high",
                "description": f"PF amount ({pf_amount}) doesn't match expected calculation ({expected_pf})",
                "suggestion": "Recalculate PF as 12% of basic salary, capped at 15,000"
            })
        
        # Check ESI anomalies
        esi_amount = salary_breakdown.deduction_components.esi
        gross_salary = salary_breakdown.gross_salary
        
        if gross_salary <= 21000 and esi_amount == 0:
            anomalies.append({
                "type": "rule_based",
                "category": "esi",
                "severity": "high",
                "description": "ESI deduction missing for employee eligible for ESI",
                "suggestion": "Add ESI deduction (0.75% of gross salary)"
            })
        elif gross_salary > 21000 and esi_amount > 0:
            anomalies.append({
                "type": "rule_based",
                "category": "esi",
                "severity": "high",
                "description": "ESI deduction applied for employee not eligible for ESI",
                "suggestion": "Remove ESI deduction for salary above 21,000"
            })
        
        # Check TDS anomalies
        tds_amount = salary_breakdown.deduction_components.tds
        annual_salary = gross_salary * 12
        
        if annual_salary > 300000 and tds_amount == 0:
            anomalies.append({
                "type": "rule_based",
                "category": "tds",
                "severity": "high",
                "description": "TDS missing for employee above tax threshold",
                "suggestion": "Calculate and apply TDS based on income tax slabs"
            })
        
        return anomalies
    
    def _detect_ai_anomalies(self, salary_breakdown, compliance_status) -> List[Dict[str, Any]]:
        """Use LLM to detect intelligent anomalies"""
        
        prompt = PromptTemplate(
            input_variables=["salary_breakdown", "compliance_status"],
            template="""
            Analyze the following salary breakdown and compliance status for potential anomalies.
            
            Salary Breakdown:
            {salary_breakdown}
            
            Compliance Status:
            {compliance_status}
            
            Look for:
            1. Unusual salary patterns
            2. Incorrect tax calculations
            3. Missing statutory deductions
            4. Excessive allowances
            5. Compliance violations
            6. Data entry errors
            
            Return a JSON response with detected anomalies:
            {{
                "anomalies": [
                    {{
                        "type": "ai_detected",
                        "category": "category_name",
                        "severity": "low/medium/high",
                        "description": "Detailed description of the anomaly",
                        "suggestion": "Recommended action to fix"
                    }}
                ]
            }}
            """
        )
        
        try:
            response = self.llm.invoke(
                prompt.format(
                    salary_breakdown=str(salary_breakdown.dict()),
                    compliance_status=str(compliance_status.dict()) if compliance_status else "None"
                )
            )
            
            json_data = self._parse_json_response(response.content)
            return json_data.get("anomalies", [])
            
        except Exception as e:
            print(f"Warning: AI anomaly detection failed: {e}")
            return []
    
    def _determine_risk_level(self, anomalies: List[Dict[str, Any]]) -> str:
        """Determine overall risk level based on anomalies"""
        if not anomalies:
            return "low"
        
        high_severity = sum(1 for a in anomalies if a.get("severity") == "high")
        medium_severity = sum(1 for a in anomalies if a.get("severity") == "medium")
        
        if high_severity > 0:
            return "high"
        elif medium_severity > 2:
            return "medium"
        else:
            return "low"
    
    def _generate_flags(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate human-readable flags from anomalies"""
        flags = []
        
        for anomaly in anomalies:
            category = anomaly.get("category", "unknown")
            severity = anomaly.get("severity", "low")
            description = anomaly.get("description", "")
            
            flag = f"[{severity.upper()}] {category}: {description}"
            flags.append(flag)
        
        return flags
    
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
            return {"anomalies": []} 