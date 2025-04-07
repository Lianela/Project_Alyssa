# active_memory.py
from long_term_memory import LongTermMemoryFile

class ActiveMemoryFile:
    def __init__(self, threshold=25, summary_size=3):
        self.location = "Science class"
        self.current_action = "Sitting with the user after being paired for a project"
        self.memories = []
        self.threshold = threshold
        self.summary_size = summary_size
        self.long_term_file = LongTermMemoryFile()
        self.message_count = 0
        self.important_keywords = ["project", "park", "school", "relationship", "conflict", "emotion", "together"]

    def add_memory(self, memory):
        self.memories.append(memory)
        self.message_count += 1
        if len(self.memories) >= self.threshold:
            self.compress_and_send()
        if self.message_count >= 100:
            print(f"Reached 100 messages. Total archived: {len(self.long_term_file.get_all_memories())}")

    def compress_and_send(self):
        batch = self.memories[:self.threshold]
        important = [m for m in batch if any(keyword in m.lower() for keyword in self.important_keywords)]
        if len(important) >= self.summary_size:
            compressed = important[:self.summary_size]
        else:
            compressed = important + batch[-(self.summary_size - len(important)):]
        self.long_term_file.store(compressed)
        self.memories = self.memories[self.threshold:]

    def update_location(self, location):
        self.location = location
        self.add_memory(f"Moved to {location}.")

    def update_action(self, action):
        self.current_action = action
        self.add_memory(f"Started {action.lower()}.")

    def current_state(self):
        context_memories = self.long_term_file.get_all_memories() + self.memories
        return {
            "location": self.location,
            "action": self.current_action,
            "recent_memories": " | ".join(context_memories[-3:])
        }