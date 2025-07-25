from typing import Dict
from lumapps_poc.infrastructure.run_context import RunContext

# Shared state dictionary keyed by a unique run_id
run_contexts: Dict[str, RunContext] = {}