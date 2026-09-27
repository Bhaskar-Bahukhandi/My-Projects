import os
from google import genai
import sys

# Ensure local imports work cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.agent import BaseAgent
from src.core.message_bus import Message, AsyncMessageBus

class PlannerAgent(BaseAgent):
    """
    The Planner Agent receives high-level tasks and breaks them down into
    sequential, actionable steps for the Worker Agent.
    """
    def __init__(self, message_bus: AsyncMessageBus):
        super().__init__(name="Planner", role="Task Decomposer", message_bus=message_bus)
        
        # Initialize Google GenAI Client
        # Falls back to GEMINI_API_KEY environment variable automatically
        self.client = genai.Client()
        
    async def process_message(self, message: Message):
        # Only process messages explicitly asking to plan a task
        if message.metadata.get("action") != "plan_task":
            return
            
        print(f"\n[Planner] Analyzing high-level task: {message.content[:50]}...")
        
        # System instructions to enforce output format
        prompt = f"""
        You are an expert Software Architect. Break down the following user request into 
        exactly 3 sequential, actionable steps for a junior developer to execute.
        
        User Request: {message.content}
        
        Output format: Just the 3 steps, numbered. No pleasantries or conversational text.
        """
        
        # Use a "pro" reasoning model for architecture and planning
        response = self.client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        
        plan_text = response.text
        
        # Route the finalized plan to the Worker Agent
        await self.send(
            content=plan_text,
            receiver_id="Worker",
            metadata={"action": "execute_plan"}
        )
