import asyncio
import uuid
import logging
import threading
from typing import Any, Dict
from fastapi import APIRouter, Body, HTTPException
from starlette.responses import StreamingResponse
from lumapps_poc.usecase.crew import LumappsPoc
from lumapps_poc.infrastructure import state_manager
from lumapps_poc.infrastructure.run_context import RunContext
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/crew",
    tags=["crew"],
)

async def sse_generator(run_id: str):
    """Generator for Server-Sent Events."""
    context = state_manager.run_contexts.get(run_id)
    if not context:
        yield f"data: Error: Run ID {run_id} not found.\n\n"
        return

    try:
        while True:
            message = await context.sse_queue.get()
            logger.info(f"[{run_id}] SSE Generator: Sending message: {message}")
            if message == "END":
                yield f"data: {message}\n\n"
                break
            yield f"data: {message}\n\n"
    except asyncio.CancelledError:
        # Handle client disconnection
        pass

@router.post("/start", status_code=202)
async def start_crew(data: Dict[str, Any] = Body(...)) -> Dict[str, str]:
    """
    Start a new crew run and get a run_id.
    """
    run_id = str(uuid.uuid4())
    topic = data.get("topic", "AI LLMs")

    # Initialize state for this run
    context = RunContext()
    context.main_loop = asyncio.get_running_loop()
    state_manager.run_contexts[run_id] = context

    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year),
    }

    crew = LumappsPoc().crew(run_context=context)

    async def run_and_cleanup():
        logger.info(f"[{run_id}] Starting crew execution...")
        try:
            await crew.kickoff_async(inputs=inputs)
            await context.sse_queue.put(f"INFO: Starting Execution")
        except Exception as e:
            await context.sse_queue.put(f"ERROR: {e}")
        finally:
            await context.sse_queue.put("END")

    asyncio.create_task(run_and_cleanup())
    
    return {"run_id": run_id}

@router.get("/{run_id}/stream")
async def stream_crew_status(run_id: str):
    """
    Stream status updates for a given crew run.
    """
    return StreamingResponse(sse_generator(run_id), media_type="text/event-stream")

@router.post("/{run_id}/input", status_code=200)
async def submit_human_input(run_id: str, data: Dict[str, Any] = Body(...)):
    """
    Submit human input to a paused crew.
    """
    context = state_manager.run_contexts.get(run_id)
    if not context:
        raise HTTPException(status_code=404, detail="Run ID not found")

    human_input = data.get("input")
    if human_input is None:
        raise HTTPException(status_code=400, detail="Input not provided")

    logger.info(f"[{run_id}] Received human input: {human_input}")
    context.human_input = human_input
    context.human_input_event.set()
    logger.info(f"[{run_id}] Event set for thread.")
    return {"message": "Input received"}
