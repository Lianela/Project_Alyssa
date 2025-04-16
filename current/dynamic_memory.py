# dynamic_memory.py
# Removed: from logic import RPLogic - Breaks circular import
# No direct import of RPLogic needed here.
# ActiveMemoryFile instance will be passed into methods requiring it.

class DynamicMemory:
    def __init__(self):
        self.location = "Science class"
        self.current_action = "Sitting with the user after being paired for a project"
        self.memories = []
        self.max_events = 3  # Small capacity for short-term memory
        self.relevance_keywords = ["hug", "tears", "sorry", "together", "project", "conflict", "emotion"]

    # active_memory object is passed as an argument
    def add_memory(self, memory, active_memory):
        """Adds a memory event and transfers older relevant events to active memory."""
        self.memories.append(memory)

        # Check relevance *before* potentially transferring to active memory
        is_relevant = self._is_relevant(memory)

        # Transfer older memories if capacity exceeded
        if len(self.memories) > self.max_events:
            # Transfer the oldest memory if it's relevant and not already in active memory
            oldest_memory = self.memories.pop(0) # Get and remove the oldest
            if self._is_relevant(oldest_memory) and oldest_memory not in active_memory.memories:
                 active_memory.add_memory(oldest_memory)
        # If the *newly added* memory is relevant and wasn't transferred above, add it now.
        # This handles the case where max_events is not exceeded yet.
        elif is_relevant and memory not in active_memory.memories:
             active_memory.add_memory(memory)


    def _is_relevant(self, memory):
        """Check if a memory is relevant based on keywords."""
        memory_lower = memory.lower()
        return any(keyword in memory_lower for keyword in self.relevance_keywords)

    # active_memory object is passed as an argument
    def update_location(self, location, active_memory):
        """Updates the current location and adds a memory event."""
        if self.location != location: # Only update if location changes
            self.location = location
            self.add_memory(f"Moved to {location}.", active_memory)

    # active_memory object is passed as an argument
    def update_action(self, action, active_memory):
        """Updates the current action and adds a memory event."""
        if self.current_action != action: # Only update if action changes
            self.current_action = action
            self.add_memory(f"Started {action.lower()}.", active_memory)

    def summarize_history(self):
        """Returns a string summarizing the most recent memory events."""
        return "Summary of recent events: " + " | ".join(self.memories) # Uses current self.memories

    def current_state(self):
        """Returns the current state including location, action, and recent memories."""
        return {
            "location": self.location,
            "action": self.current_action,
            # Ensure memories are joined correctly, even if empty
            "recent_memories": " | ".join(self.memories) if self.memories else ""
        }