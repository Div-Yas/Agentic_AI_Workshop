#!/usr/bin/env python3
"""
Test script to verify the payroll system setup
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    from app.config import settings
    
    print(f"✅ Model: {settings.MODEL_NAME}")
    print(f"✅ Temperature: {settings.TEMPERATURE}")
    print(f"✅ Max Tokens: {settings.MAX_TOKENS}")
    print(f"✅ API Key: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Missing'}")
    
    return settings.GOOGLE_API_KEY != ""

def test_llm_connection():
    """Test LLM connection"""
    print("\n🤖 Testing LLM connection...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from app.config import settings
        
        llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        
        # Simple test prompt
        response = llm.invoke("Say 'Hello from Payroll System!' in one word.")
        print(f"✅ LLM Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ LLM Test Failed: {e}")
        return False

def test_models():
    """Test Pydantic models"""
    print("\n📋 Testing data models...")
    
    try:
        from app.models.payroll import ContractData, SalaryComponent, WorkflowStatus
        
        # Test salary component
        salary = SalaryComponent(
            basic_salary=50000.0,
            hra=20000.0,
            lta=8000.0
        )
        print(f"✅ Salary Component: {salary.basic_salary}")
        
        # Test workflow status
        status = WorkflowStatus.PENDING
        print(f"✅ Workflow Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Models Test Failed: {e}")
        return False

def test_agent():
    """Test agent creation"""
    print("\n🤖 Testing agent creation...")
    
    try:
        from app.agents.contract_reader import ContractReaderAgent
        
        agent = ContractReaderAgent()
        print(f"✅ Agent Created: {agent.name}")
        print(f"✅ Agent Description: {agent.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent Test Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Payroll System Setup Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("LLM Connection", test_llm_connection),
        ("Data Models", test_models),
        ("Agent Creation", test_agent),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} Test Failed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! System is ready for development.")
        print("\nNext steps:")
        print("1. Create sample contract files in data/uploads/")
        print("2. Run: uvicorn app.main:app --reload")
        print("3. Open: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 