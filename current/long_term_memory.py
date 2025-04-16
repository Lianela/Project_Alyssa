import logging

logger = logging.getLogger()

class LongTermMemoryFile:
    def __init__(self):
        self.memory = []

    def add_event(self, event):
        if event not in self.memory:
            self.memory.append(event)
            logger.info(f"Added long-term memory: {event}")

    def get_memories(self):
        return self.memory

    def clear_memory(self):
        self.memory = []