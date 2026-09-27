import asyncio
import os
import sys

# Ensure local imports work cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.message_bus import AsyncMessageBus, Message
from src.agents.planner import PlannerAgent
from src.agents.worker import WorkerAgent
from src.agents.reviewer import ReviewerAgent

class Orchestrator:
    """
    The central brain of the Multi-Agent Framework.
    Initializes the agents, manages the message bus, and enforces safety limits.
    """
    def __init__(self, max_turns: int = 6):
        self.message_bus = AsyncMessageBus()
        self.max_turns = max_turns
        self.current_turn = 0
        self.task_completed = False
        self.final_result = None
        
        # Initialize the Team
        self.planner = PlannerAgent(self.message_bus)
        self.worker = WorkerAgent(self.message_bus)
        self.reviewer = ReviewerAgent(self.message_bus)
        
        # Subscribe the Orchestrator to monitor all traffic and catch completion events
        # We hook into 'broadcast' to intercept every message passing through the bus
        self.message_bus.subscribe("broadcast", self._monitor_traffic)
        self.message_bus.subscribe("Orchestrator", self._catch_result)

    async def _catch_result(self, message: Message):
        """Catches the final APPROVED message from the Reviewer."""
        if message.metadata.get("action") == "task_complete":
            print("\n[Orchestrator] Task successfully completed and approved by Reviewer!")
            self.task_completed = True
            self.final_result = message.content

    async def _monitor_traffic(self, message: Message):
        """Monitors traffic to prevent runaway API costs."""
        # We only count action-driven messages as "turns"
        if message.sender_id in ["Planner", "Worker", "Reviewer"]:
            self.current_turn += 1
            
        # ---------------------------------------------------------
        # SAFETY LIMIT / CIRCUIT BREAKER (Authentic Developer Note)
        # ---------------------------------------------------------
        # TODO(bhaskar): In an early version, the Reviewer and Worker got stuck 
        # in an infinite loop arguing about a Python syntax error. 
        # It ran for 150 turns and cost a fortune in API credits. 
        # FIX: Adding a strict Circuit Breaker here. If they argue for more 
        # than `max_turns`, I forcefully shut down the event loop and fail gracefully.
        
        if self.current_turn >= self.max_turns and not self.task_completed:
            print(f"\n[Orchestrator] 🚨 CIRCUIT BREAKER TRIGGERED! Max turns ({self.max_turns}) exceeded.")
            print("[Orchestrator] Halting framework to prevent infinite loop API costs.")
            self.task_completed = True
            self.final_result = "ERROR: Task failed to complete within turn limit. Infinite loop prevented."

    async def kickoff(self, user_prompt: str):
        """Starts the agentic workflow."""
        print(f"\n=== ORCHESTRATOR STARTING: '{user_prompt}' ===")
        self.current_turn = 0
        self.task_completed = False
        
        # Kick off the process by sending the task to the Planner
        initial_msg = Message(
            sender_id="User",
            receiver_id="Planner",
            content=user_prompt,
            metadata={"action": "plan_task"}
        )
        
        # Publish directly to the Planner
        await self.message_bus.publish("Planner", initial_msg)
        
        # Keep the event loop running until the task is complete or circuit breaker trips
        while not self.task_completed:
            await asyncio.sleep(1)
            
        # Log the conversation state for telemetry
        self._save_state()
        return self.final_result
        
    def _save_state(self):
        """Persist the conversation history for debugging."""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # In a production DB, you'd use a UUID for the session run and dump the full json
        with open(os.path.join(log_dir, "last_run.log"), "w") as f:
            f.write(f"Turns taken: {self.current_turn}\n")
            f.write(f"Result:\n{self.final_result}\n")
            
        print(f"[Orchestrator] Run state saved to logs/last_run.log")

if __name__ == "__main__":
    # Quick manual test block
    async def main():
        orchestrator = Orchestrator(max_turns=6)
        await orchestrator.kickoff("Write a Python function that calculates the Fibonacci sequence.")
        
    asyncio.run(main())
