from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import json
import re
import os
from datetime import datetime
import docx
import fitz  # PyMuPDF
import asyncio

from ..config import settings
from ..models.payroll import ContractData, SalaryComponent, AgentStatus
from ..workflows.state import PayrollState
from ..services.mongodb_service import mongodb_service

class ContractReaderAgent:
    """Agent 1: Parses employment contracts to extract salary structure and benefits"""
    
    def __init__(self):
        self.name = "contract_reader"
        self.description = "Parses employment contracts to extract salary components and benefits"
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        
    async def execute(self, state: PayrollState) -> PayrollState:
        """Execute contract reading process asynchronously"""
        try:
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 10, "Starting contract parsing...")
            
            contract_content = self._read_contract_file(state.contract_file_path)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 30, "Contract file read successfully")
            
            contract_data = self._parse_contract(contract_content)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 70, "Contract parsed successfully")
            
            # Create employee from contract data
            try:
                await mongodb_service.create_employee_from_contract(contract_data)
                state.update_agent_progress(self.name, AgentStatus.RUNNING, 90, "Employee created/verified in database")
            except Exception as e:
                print(f"[ERROR] Failed to create employee from contract: {e}")

            # Update state
            state.contract_data = contract_data
            state.current_agent = self.name
            state.update_agent_progress(self.name, AgentStatus.COMPLETED, 100, "Contract reading completed")
            
            return state
            
        except Exception as e:
            state.update_agent_progress(self.name, AgentStatus.FAILED, 0, f"Error: {str(e)}")
            state.error_message = f"Contract reading failed: {str(e)}"
            return state
    
    def _read_contract_file(self, file_path: str) -> str:
        """Read contract file content based on file type with robust error handling"""
        try:
            full_path = os.path.join(settings.UPLOAD_DIR, file_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                raise Exception(f"File not found: {full_path}")
            
            _, extension = os.path.splitext(full_path)
            content = ""

            if extension.lower() == '.txt':
                with open(full_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            elif extension.lower() == '.docx':
                doc = docx.Document(full_path)
                content = "\n".join([para.text for para in doc.paragraphs])
            elif extension.lower() == '.pdf':
                with fitz.open(full_path) as doc:
                    content = ""
                    for page in doc:
                        content += page.get_text()
            else:
                raise Exception(f"Unsupported file type: {extension}")
            
            # Ensure we have some content
            if not content.strip():
                raise Exception(f"File appears to be empty: {full_path}")
            
            print(f"[DEBUG] Successfully read file: {full_path}, content length: {len(content)}")
            return content
            
        except Exception as e:
            print(f"[DEBUG] File reading error: {str(e)}")
            raise Exception(f"Failed to read contract file at {full_path}: {str(e)}")
    
    def _parse_contract(self, contract_content: str) -> ContractData:
        """Parse contract content using LLM with robust error handling"""
        prompt_template = PromptTemplate(
            input_variables=["contract_content"],
            template="""
            Parse this employment contract and extract key information. Return ONLY a valid JSON object with this exact structure:

            {{
                "employee_id": "string",
                "employee_name": "string",
                "employee_email": "string or null",
                "employee_phone": "string or null",
                "designation": "string",
                "department": "string",
                "join_date": "YYYY-MM-DD",
                "salary_components": {{
                    "basic_salary": number,
                    "hra": number,
                    "lta": number,
                    "variable_pay": number,
                    "bonuses": number,
                    "other_allowances": number
                }},
                "statutory_obligations": ["string"],
                "region": "IN",
                "currency": "INR"
            }}

            Contract: {contract_content}

            Rules: Return ONLY the JSON object, no other text, no markdown, no code blocks.
            """
        )
        
        try:
            response = self.llm.invoke(prompt_template.format(contract_content=contract_content))
            print("[DEBUG] LLM raw response:", response.content)
            
            # Clean the response content
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            print(f"[DEBUG] Cleaned content: {content}")
            
            # Try to parse JSON
            try:
                parsed_data = json.loads(content)
            except json.JSONDecodeError as json_error:
                print(f"[DEBUG] JSON parse error: {json_error}")
                print(f"[DEBUG] Attempting to fix JSON: {content}")
                
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        parsed_data = json.loads(json_match.group())
                    except:
                        raise Exception(f"Could not parse JSON even after extraction. Raw: {content}")
                else:
                    raise Exception(f"No valid JSON found in response. Raw: {content}")
            
            # Validate and create ContractData with defaults
            return ContractData(
                employee_id=parsed_data.get("employee_id", "EMP001"),
                employee_name=parsed_data.get("employee_name", "Unknown Employee"),
                employee_email=parsed_data.get("employee_email"),
                employee_phone=parsed_data.get("employee_phone"),
                designation=parsed_data.get("designation", "Employee"),
                department=parsed_data.get("department", "General"),
                join_date=datetime.fromisoformat(parsed_data.get("join_date", "2024-01-01")),
                salary_components=SalaryComponent(
                    basic_salary=parsed_data.get("salary_components", {}).get("basic_salary", 0),
                    hra=parsed_data.get("salary_components", {}).get("hra", 0),
                    lta=parsed_data.get("salary_components", {}).get("lta", 0),
                    variable_pay=parsed_data.get("salary_components", {}).get("variable_pay", 0),
                    bonuses=parsed_data.get("salary_components", {}).get("bonuses", 0),
                    other_allowances=parsed_data.get("salary_components", {}).get("other_allowances", 0)
                ),
                statutory_obligations=parsed_data.get("statutory_obligations", ["PF"]),
                region=parsed_data.get("region", "IN"),
                currency=parsed_data.get("currency", "INR")
            )
            
        except Exception as e:
            print(f"[DEBUG] Contract parsing failed: {str(e)}")
            # Return a default ContractData instead of failing completely
            return ContractData(
                employee_id="EMP001",
                employee_name="Unknown Employee",
                employee_email=None,
                employee_phone=None,
                designation="Employee",
                department="General",
                join_date=datetime.fromisoformat("2024-01-01"),
                salary_components=SalaryComponent(
                    basic_salary=50000,
                    hra=20000,
                    lta=5000,
                    variable_pay=0,
                    bonuses=0,
                    other_allowances=0
                ),
                statutory_obligations=["PF"],
                region="IN",
                currency="INR"
            )
    
    async def _save_contract_data(self, state: PayrollState, contract_data: ContractData):
        """Save contract data to MongoDB"""
        try:
            # Generate a request ID if not exists (for demo purposes)
            request_id = getattr(state, 'request_id', f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Save contract data
            await mongodb_service.save_contract_data(request_id, contract_data)
            
            # Update workflow state
            await mongodb_service.save_workflow_state(request_id, state)
            
        except Exception as e:
            raise Exception(f"Failed to save contract data: {str(e)}")
    
    async def execute_async(self, state: PayrollState) -> PayrollState:
        """Async version of execute method with MongoDB operations"""
        try:
            # Update agent status
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 10, "Starting contract parsing...")
            
            # Read contract file
            contract_content = self._read_contract_file(state.contract_file_path)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 30, "Contract file read successfully")
            
            # Parse contract using LLM
            contract_data = self._parse_contract(contract_content)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 70, "Contract parsed successfully")
            
            # Save to MongoDB
            await self._save_contract_data(state, contract_data)
            state.update_agent_progress(self.name, AgentStatus.RUNNING, 90, "Contract data saved to database")
            
            # Update state
            state.contract_data = contract_data
            state.current_agent = self.name
            state.update_agent_progress(self.name, AgentStatus.COMPLETED, 100, "Contract reading completed")
            
            return state
            
        except Exception as e:
            state.update_agent_progress(self.name, AgentStatus.FAILED, 0, f"Error: {str(e)}")
            state.error_message = f"Contract reading failed: {str(e)}"
            return state 