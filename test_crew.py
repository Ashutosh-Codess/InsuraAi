import os
import sys
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, '.env'))

sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'backend'))

from agents.orchestrator import dispatch_claim_workflow

try:
    print('Testing claim adjudication...')
    result = dispatch_claim_workflow('claim_adjudication', 'Test claim for 5000')
    print('Result:', result)
except Exception as e:
    print('Error:', e)
