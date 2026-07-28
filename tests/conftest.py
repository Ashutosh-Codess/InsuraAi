"""Test-wide settings that must be applied before FastAPI is imported."""

import os


# Health and authentication tests don't need the optional AI model or vector
# database. Skipping their startup work keeps the suite deterministic offline.
os.environ.setdefault("INSURAMIND_SKIP_AI_STARTUP", "1")
