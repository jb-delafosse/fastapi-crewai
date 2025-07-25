import asyncio
import logging
from typing import Type, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from lumapps_poc.infrastructure.run_context import RunContext

logger = logging.getLogger(__name__)

class AskHumanToolSchema(BaseModel):
    """Input for AskHumanTool."""
    prompt: str = Field(description="The question or prompt to ask the human for input.")

class AskHumanTool(BaseTool):
    name: str = "Ask Human for Input"
    description: str = "Asks a human for input on a specific prompt and waits for their response. Use this when you need a human's opinion or decision."
    args_schema: Type[BaseModel] = AskHumanToolSchema
    run_context: RunContext | None = None

    def _run(self, prompt: str) -> Any:
        if not self.run_context:
            return "Error: run_context not configured for AskHumanTool."

        # Signal that human input is needed
        logger.info(f"Sending prompt to human: {prompt}")
        # We need to run the async put in the main event loop
        if self.run_context.main_loop:
            asyncio.run_coroutine_threadsafe(
                self.run_context.sse_queue.put(f"PROMPT:{prompt}"),
                self.run_context.main_loop
            )

        # Clear the event and wait for it to be set
        self.run_context.human_input_event.clear()
        logger.info("Waiting for human input...")
        self.run_context.human_input_event.wait()
        logger.info("Human input event received.")

        human_response = self.run_context.human_input
        self.run_context.human_input = None  # Clear the input

        logger.info(f"Retrieved human response: {human_response}")
        return f"The human responded: {human_response}"