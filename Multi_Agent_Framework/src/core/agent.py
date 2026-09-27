import asyncio
from abc import ABC, abstractmethod
import sys
import os

# Add project root to sys path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.message_bus import AsyncMessageBus, Message

class BaseAgent(ABC):
    """
    Abstract base class for all specialized AI agents in the orchestration framework.
    Forces all subclassed agents to implement a `process_message` event listener.
    """
    def __init__(self, name: str, role: str, message_bus: AsyncMessageBus):
        self.name = name
        self.role = role
        self.message_bus = message_bus
        
        # Local state holding conversation history
        self.history = []
        
        # Subscribe to global broadcasts and direct messages addressed to this agent's name
        self.message_bus.subscribe("broadcast", self._inbox_handler)
        self.message_bus.subscribe(self.name, self._inbox_handler)
        
    async def _inbox_handler(self, message: Message):
        """Internal handler that catches messages from the bus and routes them."""
        # Agents shouldn't process their own echoes
        if message.sender_id == self.name:
            return
            
        self.history.append(message)
        
        # Trigger the child class's specific AI logic
        await self.process_message(message)

    @abstractmethod
    async def process_message(self, message: Message):
        """
        Must be implemented by child classes (e.g., PlannerAgent, WorkerAgent). 
        Defines how the agent queries the LLM and reacts to an incoming message.
        """
        pass

    async def send(self, content: str, receiver_id: str = "broadcast", metadata: dict = None):
        """Publishes a message to the bus for other agents to consume."""
        msg = Message(
            sender_id=self.name,
            receiver_id=receiver_id,
            content=content,
            metadata=metadata or {}
        )
        
        # Route to specific agent or broadcast to all
        topic = receiver_id
        await self.message_bus.publish(topic, msg)
        
        # Keep a local copy of sent messages
        self.history.append(msg)
        
        # Terminal visualizer
        preview = content[:75].replace('\n', ' ') + ('...' if len(content) > 75 else '')
        print(f"[{self.name} -> {receiver_id}]: {preview}")
