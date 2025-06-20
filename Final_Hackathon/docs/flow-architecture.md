# Data Flow Architecture: Frontend → Backend → Agents

## 🔄 Complete System Flow

### 1. **Frontend Initiation**
```
User Uploads Contract → React Component → API Service → FastAPI Endpoint
```

**Frontend Flow:**
1. **ContractUpload.js** - Drag & drop interface for PDF/DOCX files
2. **useUpload.js** - Manages upload state and progress
3. **upload.js** - API service for file upload
4. **WebSocket connection** - Real-time progress updates

### 2. **Backend Processing**
```
FastAPI Endpoint → File Validation → LangGraph Workflow → Multi-Agent Pipeline
```

**Backend Flow:**
1. **upload.py** - Handles file upload and validation
2. **routes.py** - Main API endpoints
3. **payroll_workflow.py** - LangGraph workflow orchestration
4. **WebSocket** - Real-time status updates to frontend

### 3. **Multi-Agent Workflow**
```
Agent 1 → Agent 2 → Agent 3 → Agent 4 → Agent 5 → Results Storage
```

## 📊 Detailed Flow Breakdown

### **Phase 1: File Upload & Validation**
```
Frontend: ContractUpload.js
    ↓ (File + Metadata)
Backend: /api/v1/upload/contract
    ↓ (File Validation)
Backend: File Storage (data/uploads/)
    ↓ (Workflow Trigger)
LangGraph: payroll_workflow.py
```

### **Phase 2: Agent 1 - Contract Reader**
```
Input: PDF/DOCX Contract File
    ↓
LangGraph: contract_reader.py
    ↓
Tools: PDF/DOCX Parser + OCR
    ↓
Gemini 1.5 Flash: Text Analysis
    ↓
Output: Structured JSON (salary_components, benefits, clauses)
    ↓
State Update: contract_data
```

### **Phase 3: Agent 2 - Salary Calculator**
```
Input: Structured Contract Data
    ↓
LangGraph: salary_calculator.py
    ↓
Logic: Salary computation + Deductions
    ↓
Gemini 1.5 Flash: Calculation validation
    ↓
Output: Salary breakdown (gross, net, deductions)
    ↓
State Update: salary_breakdown
```

### **Phase 4: Agent 3 - Compliance Mapper (RAG)**
```
Input: Salary breakdown + Regional requirements
    ↓
LangGraph: compliance_mapper.py
    ↓
RAG Service: Vector store query (tax_rules, compliance_docs)
    ↓
Gemini 1.5 Flash: Rule mapping + validation
    ↓
Output: Compliance validation + corrections
    ↓
State Update: compliance_status
```

### **Phase 5: Agent 4 - Anomaly Detector**
```
Input: Complete payroll data + Historical data
    ↓
LangGraph: anomaly_detector.py
    ↓
Analysis: Statistical + AI-powered detection
    ↓
Gemini 1.5 Flash: Anomaly reasoning
    ↓
Output: Anomaly report + flags
    ↓
State Update: anomalies
```

### **Phase 6: Agent 5 - Document Generator**
```
Input: Validated payroll data + Templates
    ↓
LangGraph: document_generator.py
    ↓
Tools: PDF generation + Template engine
    ↓
Gemini 1.5 Flash: Content formatting
    ↓
Output: Payslips + Tax forms (PDF)
    ↓
State Update: documents
```

## 🔄 Real-time Communication Flow

### **WebSocket Flow:**
```
Frontend: useWebSocket.js
    ↓ (Connection)
Backend: websocket.py
    ↓ (Event Handling)
LangGraph: State updates
    ↓ (Progress Events)
Frontend: Real-time UI updates
```

### **Progress Tracking:**
```
Workflow Start → Agent 1 (20%) → Agent 2 (40%) → Agent 3 (60%) → Agent 4 (80%) → Agent 5 (100%)
    ↓              ↓              ↓              ↓              ↓              ↓
WebSocket      WebSocket      WebSocket      WebSocket      WebSocket      WebSocket
Update         Update         Update         Update         Update         Update
```

## 🗄️ Data Storage Flow

### **Temporary Storage:**
```
Uploads: data/uploads/ (contract files)
Outputs: data/outputs/ (generated documents)
```

### **Persistent Storage:**
```
PostgreSQL: Employee data, payroll history, compliance records
ChromaDB: Tax rules, compliance documents (RAG)
Redis: Session data, workflow state caching
```

## 🚨 Error Handling Flow

### **Agent Failure:**
```
Agent Error → LangGraph Error Handler → Rollback State → Retry Logic → Alternative Path
    ↓              ↓                      ↓              ↓              ↓
WebSocket      Error Logging          State Reset    Retry Agent    Continue Workflow
Error Event    (Database)             (Redis)        (Max 3x)       (Skip if critical)
```

### **Frontend Error Handling:**
```
API Error → Error Boundary → User Notification → Retry Option → Fallback UI
```

## 📈 State Management Flow

### **LangGraph State:**
```python
class PayrollState:
    # Input
    employee_id: str
    contract_file: str
    
    # Agent Outputs
    contract_data: Dict
    salary_breakdown: Dict
    compliance_status: Dict
    anomalies: List
    documents: List
    
    # Workflow Control
    current_agent: str
    workflow_status: str
    error_message: str
```

### **Frontend State:**
```javascript
// PayrollContext.js
{
  upload: { file, progress, status },
  workflow: { currentStep, progress, status },
  results: { payroll, anomalies, documents },
  errors: { messages, retryCount }
}
```

## 🔐 Security Flow

### **File Upload Security:**
```
File Upload → Virus Scan → File Type Validation → Size Check → Secure Storage
    ↓              ↓              ↓              ↓              ↓
Frontend      Backend         Backend         Backend         Backend
Validation    Security        Validation      Validation      Storage
```

### **Data Privacy:**
```
Sensitive Data → Encryption → Secure Processing → Anonymized Storage → Audit Trail
    ↓              ↓              ↓              ↓              ↓
Input          Backend         Agents          Database        Logging
```

## 🎯 Key Integration Points

### **1. Frontend-Backend Integration:**
- REST API for file upload and status queries
- WebSocket for real-time progress updates
- File download for generated documents

### **2. Backend-Agent Integration:**
- LangGraph workflow orchestration
- State management across agents
- Error handling and recovery

### **3. Agent-AI Integration:**
- Gemini 1.5 Flash for text processing
- LangChain tools for document operations
- RAG for compliance knowledge retrieval

### **4. Data Integration:**
- PostgreSQL for structured data
- ChromaDB for vector storage
- Redis for caching and sessions

This architecture ensures scalable, maintainable, and robust payroll processing with real-time updates and comprehensive error handling! 🚀 