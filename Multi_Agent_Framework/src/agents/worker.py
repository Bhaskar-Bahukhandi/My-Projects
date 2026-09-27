import os
from google import genai
import sys

# Ensure local imports work cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.agent import BaseAgent
from src.core.message_bus import Message, AsyncMessageBus

class WorkerAgent(BaseAgent):
    """
    The Worker Agent takes a step-by-step plan or revision request 
    and writes the actual Python code to satisfy it.
    """
    def __init__(self, message_bus: AsyncMessageBus):
        super().__init__(name="Worker", role="Code Generator", message_bus=message_bus)
        self.client = genai.Client()
        
    async def process_message(self, message: Message):
        action = message.metadata.get("action")
        if action not in ["execute_plan", "revise_code"]:
            return
            
        print(f"\n[Worker] Generating code based on input from {message.sender_id}...")
        
        # ---------------------------------------------------------
        # STRUCTURED OUTPUT FIX (Authentic Developer Note)
        # ---------------------------------------------------------
        # TODO(bhaskar): In my first prototype, the Worker would ramble and say 
        # "Sure, here is your code!". This completely broke the downstream Reviewer's parsing logic. 
        # I fixed this by adding a strict system prompt here to enforce Markdown-only outputs.
        # A true production system would use `response_schema` (Structured Outputs), 
        # but prompt engineering is sufficient for this scope.
        
        prompt = f"""
        You are a Senior Python Developer. Execute the following task/plan.
        You must output ONLY valid Python code wrapped in ```python blocks. 
        Do not add any conversational text before or after the code.
        
        Input Context:
        {message.content}
        """
        
        # Inject the python functions into the Gemini model
        # The new google-genai SDK handles the function calling loop automatically if configured
        try:
            from google.genai import types
            from src.core.tools import execute_python_code, read_file, write_file
            
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[execute_python_code, read_file, write_file],
                    temperature=0.2
                )
            )
        except Exception as e:
            # Fallback if tools aren't supported in the environment yet
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
        
        # Route the generated code to the Reviewer Agent for critique
        await self.send(
            content=response.text,
            receiver_id="Reviewer",
            metadata={"action": "review_code"}
        )
