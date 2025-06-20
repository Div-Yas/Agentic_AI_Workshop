from ..agents import (
    ContractReaderAgent,
    SalaryCalculatorAgent,
    ComplianceMapperAgent,
    AnomalyDetectorAgent,
    DocumentGeneratorAgent,
)
from ..workflows.state import PayrollState


async def run_workflow(state: PayrollState) -> PayrollState:
    """
    Runs the payroll processing workflow by executing a sequence of agents.

    This function takes an initial payroll state, typically containing contract
    details, and passes it through a series of agents. Each agent performs a
    specific task, such as reading the contract, calculating the salary,
    checking for compliance, detecting anomalies, and finally generating
    the necessary documents.

    Args:
        state (PayrollState): The initial state of the payroll process.

    Returns:
        PayrollState: The final state after all agents have been executed.
    """

    # Initialize agents
    contract_reader = ContractReaderAgent()
    salary_calculator = SalaryCalculatorAgent()
    compliance_mapper = ComplianceMapperAgent()
    anomaly_detector = AnomalyDetectorAgent()
    document_generator = DocumentGeneratorAgent()

    # Run the workflow
    state = await contract_reader.execute(state)
    if state.error_message:
        return state

    state = await salary_calculator.execute(state)
    if state.error_message:
        return state

    state = await compliance_mapper.execute(state)
    if state.error_message:
        return state

    state = await anomaly_detector.execute(state)
    if state.error_message:
        return state

    state = await document_generator.execute(state)
    if state.error_message:
        return state

    return state 