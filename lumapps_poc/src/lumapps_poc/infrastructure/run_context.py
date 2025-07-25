import asyncio
import threading
from typing import Any, Dict, Optional

class RunContext:
    def __init__(self):
        self.sse_queue = asyncio.Queue()
        self.human_input_event = threading.Event()
        self.human_input: Optional[str] = None
        self.state: Dict[str, Any] = {}
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None