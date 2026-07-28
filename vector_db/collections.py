"""
The four knowledge base collections from the doc's Vector Knowledge Base
Specifications section. Kept as plain constants so every module that
touches the vector DB (indexer, rag_tool, agents) references the same
names instead of hardcoding strings everywhere.
"""

POLICY_TERMS = "policy_terms"
MEDICAL_RULES = "medical_rules"
REPAIR_ESTIMATES = "repair_estimates"
REGULATORY_RULES = "regulatory_rules"

ALL_COLLECTIONS = [POLICY_TERMS, MEDICAL_RULES, REPAIR_ESTIMATES, REGULATORY_RULES]
