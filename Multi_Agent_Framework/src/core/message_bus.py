import asyncio
from typing import Callable, Dict, List, Any
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Standardized message payload for inter-agent communication."""
    sender_id: str
    receiver_id: str = "broadcast"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AsyncMessageBus:
    """
    An asynchronous Pub/Sub message bus.
    
    # TODO(bhaskar): In a true production microservice architecture (like Kubernetes), 
    # I would use Redis Pub/Sub or RabbitMQ here. Since this is a lightweight 
    # local framework designed to run anywhere, I am using asyncio memory queues 
    # to entirely avoid massive external dependency bloat.
    """
    def __init__(self):
        # Maps a topic string to a list of async callbacks
        self.subscribers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, topic: str, callback: Callable):
        """Allows an agent to listen to a specific topic or direct messages."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        
    async def publish(self, topic: str, message: Message):
        """Broadcasts a message to all listeners of a topic concurrently."""
        if topic in self.subscribers:
            # Fire and forget callbacks asynchronously
            tasks = [callback(message) for callback in self.subscribers[topic]]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    import traceback
                    print(f"\n[MessageBus Error] Callback crashed: {res}")
                    traceback.print_exception(type(res), res, res.__traceback__)
