# dynamic_memory.py
class DynamicMemory:
    def __init__(self):
        self.location = "Science class"
        self.current_action = "Sitting with the user after being paired for a project"
        self.memories = []
        self.max_events = 3  # Small capacity for short-term memory
        self.relevance_keywords = ["hug", "tears", "sorry", "together", "project", "conflict", "emotion"]

    def add_memory(self, memory, active_memory):
        self.memories.append(memory)
        
        # Check if the memory is relevant
        if self._is_relevant(memory):
            active_memory.add_memory(memory)
        
        # If capacity is exceeded, send remaining relevant events to active memory and clear
        if len(self.memories) > self.max_events:
            for mem in self.memories[:-self.max_events]:
                if self._is_relevant(mem) and mem not in active_memory.memories:
                    active_memory.add_memory(mem)
            self.memories = self.memories[-self.max_events:]

    def _is_relevant(self, memory):
        """Check if a memory is relevant based on keywords."""
        memory_lower = memory.lower()
        return any(keyword in memory_lower for keyword in self.relevance_keywords)

    def update_location(self, location, active_memory):
        self.location = location
        self.add_memory(f"Moved to {location}.", active_memory)

    def update_action(self, action, active_memory):
        self.current_action = action
        self.add_memory(f"Started {action.lower()}.", active_memory)

    def summarize_history(self):
        return "Summary of recent events: " + " | ".join(self.memories)

    def current_state(self):
        return {
            "location": self.location,
            "action": self.current_action,
            "recent_memories": " | ".join(self.memories[-3:])
        }