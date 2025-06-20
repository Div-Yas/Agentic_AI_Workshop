from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import json
import re
from datetime import datetime

from ..config import settings
from ..models.payroll import SalaryBreakdown, SalaryComponent, DeductionComponent, AgentStatus
from ..workflows.state import PayrollState

class SalaryCalculatorAgent:
    """Agent 2: Computes salary breakdown and deductions"""
    
    def __init__(self):
        self.name = "salary_calculator"
        self.description = "Computes salary breakdown including gross, net, and all deductions"
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        
    async def execute(self, state: PayrollState) -> PayrollState:
        """Execute salary calculation process"""
        try:
            # Update agent status
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 10, "Starting salary calculation...")
            
            if not state.contract_data:
                raise ValueError("Contract data not available for salary calculation")
            
            # Calculate salary breakdown
            salary_breakdown = self._calculate_salary_breakdown(state.contract_data)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 70, "Salary breakdown calculated")
            
            # Validate calculations
            self._validate_salary_breakdown(salary_breakdown)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 90, "Salary calculations validated")
            
            # Update state with calculated data
            state.salary_breakdown = salary_breakdown
            state.update_agent_progress(self.name, AgentStatus.COMPLETED, 100, "Salary calculation completed")
            
            return state
            
        except Exception as e:
            state.update_agent_progress(self.name, AgentStatus.FAILED, 0, f"Error: {str(e)}")
            state.error_message = f"Salary calculation failed: {str(e)}"
            return state
    
    def _calculate_salary_breakdown(self, contract_data) -> SalaryBreakdown:
        """Calculate complete salary breakdown"""
        
        # Get salary components
        salary_comp = contract_data.salary_components
        
        # Calculate total earnings
        total_earnings = (
            salary_comp.basic_salary +
            salary_comp.hra +
            salary_comp.lta +
            salary_comp.variable_pay +
            salary_comp.bonuses +
            salary_comp.other_allowances
        )
        
        # Calculate statutory deductions
        pf_amount = min(salary_comp.basic_salary * 0.12, 15000)  # PF capped at 15,000
        esi_amount = total_earnings * 0.0075 if total_earnings <= 21000 else 0  # ESI only if salary <= 21,000
        gratuity_amount = (salary_comp.basic_salary * 4.81) / 26  # Gratuity calculation
        
        # Calculate TDS (simplified calculation)
        tds_amount = self._calculate_tds(total_earnings)
        
        # Calculate total deductions
        total_deductions = pf_amount + esi_amount + gratuity_amount + tds_amount
        
        # Calculate net salary
        net_salary = total_earnings - total_deductions
        
        # Create deduction component
        deduction_comp = DeductionComponent(
            pf=pf_amount,
            esi=esi_amount,
            gratuity=gratuity_amount,
            tds=tds_amount,
            other_deductions=0.0
        )
        
        # Create calculation justification
        justification = {
            "pf_calculation": f"PF: 12% of Basic Salary ({salary_comp.basic_salary}) = {pf_amount}, capped at 15,000",
            "esi_calculation": f"ESI: 0.75% of Gross Salary ({total_earnings}) = {esi_amount}",
            "gratuity_calculation": f"Gratuity: (Basic × 4.81) / 26 = ({salary_comp.basic_salary} × 4.81) / 26 = {gratuity_amount}",
            "tds_calculation": f"TDS: Calculated based on income tax slabs = {tds_amount}",
            "net_calculation": f"Net Salary: Gross ({total_earnings}) - Deductions ({total_deductions}) = {net_salary}"
        }
        
        return SalaryBreakdown(
            gross_salary=total_earnings,
            net_salary=net_salary,
            total_earnings=total_earnings,
            total_deductions=total_deductions,
            salary_components=salary_comp,
            deduction_components=deduction_comp,
            calculation_justification=justification
        )
    
    def _calculate_tds(self, gross_salary: float) -> float:
        """Calculate TDS based on income tax slabs (simplified)"""
        annual_salary = gross_salary * 12
        
        # Simplified tax calculation (FY 2024-25 slabs)
        if annual_salary <= 300000:
            return 0
        elif annual_salary <= 600000:
            return ((annual_salary - 300000) * 0.05) / 12
        elif annual_salary <= 900000:
            return ((15000 + (annual_salary - 600000) * 0.10) / 12)
        elif annual_salary <= 1200000:
            return ((45000 + (annual_salary - 900000) * 0.15) / 12)
        elif annual_salary <= 1500000:
            return ((90000 + (annual_salary - 1200000) * 0.20) / 12)
        else:
            return ((150000 + (annual_salary - 1500000) * 0.30) / 12)
    
    def _validate_salary_breakdown(self, salary_breakdown: SalaryBreakdown):
        """Validate salary breakdown calculations"""
        if salary_breakdown.gross_salary <= 0:
            raise ValueError("Gross salary must be greater than 0")
        
        if salary_breakdown.net_salary < 0:
            raise ValueError("Net salary cannot be negative")
        
        if salary_breakdown.total_deductions > salary_breakdown.gross_salary:
            raise ValueError("Total deductions cannot exceed gross salary")
        
        # Validate PF cap
        if salary_breakdown.deduction_components.pf > 15000:
            raise ValueError("PF amount exceeds the statutory cap of 15,000")
        
        # Validate ESI threshold
        if salary_breakdown.gross_salary > 21000 and salary_breakdown.deduction_components.esi > 0:
            raise ValueError("ESI should not be deducted for salary above 21,000") 