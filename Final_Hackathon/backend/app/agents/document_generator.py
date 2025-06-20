from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import json
import re
import os
from datetime import datetime
from fpdf import FPDF
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ..config import settings
from ..models.payroll import GeneratedDocument, AgentStatus
from ..workflows.state import PayrollState

class DocumentGeneratorAgent:
    """Agent 5: Generates payslips and tax forms"""
    
    def __init__(self):
        self.name = "document_generator"
        self.description = "Generates downloadable payslips and tax forms"
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        
    async def execute(self, state: PayrollState) -> PayrollState:
        """Execute document generation process"""
        try:
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 10, "Starting document generation...")
            
            if not state.salary_breakdown:
                raise ValueError("Salary breakdown not available")
            
            # Generate payslip
            payslip_doc = self._generate_payslip(state)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 50, "Payslip generated")
            
            # Generate tax summary
            tax_doc = self._generate_tax_summary(state)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 80, "Tax summary generated")
            
            # Add documents to state
            state.generated_documents = [payslip_doc, tax_doc]
            state.update_agent_progress(self.name, AgentStatus.COMPLETED, 100, "Document generation completed")
            
            return state
            
        except Exception as e:
            state.update_agent_progress(self.name, AgentStatus.FAILED, 0, f"Error: {str(e)}")
            state.error_message = f"Document generation failed: {str(e)}"
            return state
    
    def _generate_payslip(self, state: PayrollState) -> GeneratedDocument:
        """Generate payslip document"""
        # Create payslip content
        payslip_content = self._create_payslip_content(state)
        
        # Save to file
        file_name = f"payslip_{state.request_id}.pdf"
        file_path = os.path.join(settings.OUTPUT_DIR, file_name)
        
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        self._create_payslip_pdf(payslip_content, file_path)
        
        return GeneratedDocument(
            document_type="payslip",
            file_path=file_path,
            file_name=file_name,
            generated_at=datetime.now()
        )
    
    def _create_payslip_pdf(self, content: str, file_path: str):
        """Create a PDF document from text content"""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Encode content to latin-1, which is what FPDF uses internally
            encoded_content = content.encode('latin-1', 'replace').decode('latin-1')
            
            logger.info(f"Generating PDF with content:\n{encoded_content}")
            pdf.multi_cell(0, 10, encoded_content)
            
            pdf.output(file_path)
            logger.info(f"Successfully generated PDF: {file_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}", exc_info=True)
            raise
    
    def _generate_tax_summary(self, state: PayrollState) -> GeneratedDocument:
        """Generate tax summary document"""
        # Create tax summary content
        tax_content = self._create_tax_summary_content(state)
        
        # Save to file
        file_name = f"tax_summary_{state.employee_id}_{state.processing_month}.txt"
        file_path = os.path.join(settings.OUTPUT_DIR, file_name)
        
        with open(file_path, 'w') as f:
            f.write(tax_content)
        
        return GeneratedDocument(
            document_type="tax_summary",
            file_path=file_path,
            file_name=file_name,
            generated_at=datetime.now()
        )
    
    def _create_payslip_content(self, state: PayrollState) -> str:
        """Create payslip content"""
        contract = state.contract_data
        salary = state.salary_breakdown
        
        content = f"""
PAYSLIP - {state.processing_month}
=====================================

Employee Information:
- Employee ID: {contract.employee_id}
- Employee Name: {contract.employee_name}
- Designation: {contract.designation}
- Department: {contract.department}

Salary Breakdown:
- Basic Salary: {salary.salary_components.basic_salary}
- HRA: {salary.salary_components.hra}
- LTA: {salary.salary_components.lta}
- Variable Pay: {salary.salary_components.variable_pay}
- Bonuses: {salary.salary_components.bonuses}
- Other Allowances: {salary.salary_components.other_allowances}

Deductions:
- PF: {salary.deduction_components.pf}
- ESI: {salary.deduction_components.esi}
- TDS: {salary.deduction_components.tds}
- Gratuity: {salary.deduction_components.gratuity}

Summary:
- Gross Salary: {salary.gross_salary}
- Total Deductions: {salary.total_deductions}
- Net Salary: {salary.net_salary}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return content.strip()
    
    def _create_tax_summary_content(self, state: PayrollState) -> str:
        """Create tax summary content"""
        contract = state.contract_data
        salary = state.salary_breakdown
        compliance = state.compliance_status
        
        content = f"""
TAX SUMMARY - {state.processing_month}
=====================================

Employee: {contract.employee_name} ({contract.employee_id})

Taxable Income:
- Annual Gross Salary: {salary.gross_salary * 12}
- Annual Net Salary: {salary.net_salary * 12}

Deductions Applied:
- PF Contribution: {salary.deduction_components.pf * 12}
- ESI Contribution: {salary.deduction_components.esi * 12}
- TDS: {salary.deduction_components.tds * 12}

Compliance Status: {'Compliant' if compliance.is_compliant else 'Non-Compliant'}

Tax Slabs Applied: {compliance.tax_slabs_applied}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return content.strip() 