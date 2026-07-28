"""
Stops an agent (or a crew handing off between agents) from looping
forever. orchestrator.py should call check_iteration() on every hop.
"""
MAX_ITERATIONS = 5


class AgentLoopError(Exception):
    pass


def check_iteration(current_count: int) -> int:
    if current_count >= MAX_ITERATIONS:
        raise AgentLoopError(f"Agent execution exceeded max_iterations={MAX_ITERATIONS}")
    return current_count + 1
