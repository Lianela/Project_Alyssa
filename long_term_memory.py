# long_term_memory.py
class LongTermMemoryFile:
    def __init__(self):
        self.stored_memories = []

    def store(self, compressed_memories):
        self.stored_memories.append(compressed_memories)

    def get_all_memories(self):
        return [memory for sublist in self.stored_memories for memory in sublist]