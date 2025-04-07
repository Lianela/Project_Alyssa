# dynamic_memory.py
class DynamicMemory:
    def __init__(self):
        self.location = "Science class"
        self.current_action = "Sitting with the user after being paired for a project"
        self.memories = [
            "Poppy was annoyed when paired with Lin.",
            "She rolled her eyes when he approached.",
            "She's starting to feel something she can't explain when talking to him."
        ]

    def add_memory(self, memory):
        self.memories.append(memory)

    def update_location(self, location):
        self.location = location
        self.add_memory(f"Moved to {location}.")

    def update_action(self, action):
        self.current_action = action
        self.add_memory(f"Started {action.lower()}.")

    def summarize_history(self):
        # Summarize all events from the first message to now
        return "Summary of events: " + " | ".join(self.memories)

    def current_state(self):
        # Current location and action with the user
        return {
            "location": self.location,
            "action": self.current_action,
            "recent_memories": " | ".join(self.memories[-3:])
        }