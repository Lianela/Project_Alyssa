# logic.py
import logging
from active_memory import ActiveMemoryFile
from character_memory import CharacterMemory, UserMemory
from long_term_memory import LongTermMemoryFile
from emotionalcore import EmotionalCore
from dynamic_memory import DynamicMemory

# Set up logging
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filemode="a"
)
logger = logging.getLogger()

class RPLogic:
    def __init__(self, character_memory, active_memory, user_memory, emotional_core=None, dynamic_memory=None):
        self.character_memory = character_memory
        self.active_memory = active_memory
        self.user_memory = user_memory
        self.long_term_memory = LongTermMemoryFile()
        self.dynamic_memory = dynamic_memory if dynamic_memory is not None else DynamicMemory()
        self.emotional_core = emotional_core if emotional_core is not None else EmotionalCore()

    def update_location_and_action(self, user_input):
        user_input = user_input.lower()
        locations = ["house", "park", "library", "school", "science class"]
        actions = ["work", "continue", "plan", "relax", "start"]
        for loc in locations:
            if loc in user_input:
                self.dynamic_memory.update_location(loc.capitalize() if loc != "house" else "Poppy's House", self.active_memory)
                break
        for act in actions:
            if act in user_input:
                self.dynamic_memory.update_action(f"{act.capitalize()}ing the project", self.active_memory)
                break

    def construct_context(self, user_input):
        self.update_location_and_action(user_input)
        dyn_state = self.dynamic_memory.current_state()
        active_state = self.active_memory.current_state()
        context = {
            "location": "public" if dyn_state['location'] != "Poppy's House" else "private",
            "recent_failure": any("fail" in mem.lower() for mem in (dyn_state['recent_memories'].split(" | ") + active_state['recent_memories'].split(" | ")) if mem)
        }
        emotional_guidance = self.emotional_core.process_interaction(user_input, context)

        char_base = self.character_memory.get_character_info()
        user_state = self.user_memory.get_user_info()

        internal_thought = (
            f"[INTERNAL THOUGHT]\n{char_base['name']} is in {dyn_state['location']}. "
            f"She is currently {dyn_state['action'].lower()}. "
            f"Her emotional state is: {', '.join(emotional_guidance['emotional_state']).lower()}. "
            f"Her attitude is: {emotional_guidance['attitude'].lower()}. "
            f"Her relationship with {user_state['name']} is: {emotional_guidance['relationship'].lower()}."
        )
        logger.info(internal_thought)

        context = (
            f"Character: {char_base['name']}\n"
            f"Personality: {char_base['personality']}\n"
            f"Active Memory: Location: {dyn_state['location']} | Action: {dyn_state['action']}\n"
            f"Emotional State: {', '.join(emotional_guidance['emotional_state'])}\n"
            f"Attitude: {emotional_guidance['attitude']}\n"
            f"Relationship with {user_state['name']}: {emotional_guidance['relationship']}\n"
            f"Dynamic Memory (Recent Events): {dyn_state['recent_memories'] if dyn_state['recent_memories'] else 'None'}\n"
            f"Active Memory (Mid-Term Events): {active_state['recent_memories'] if active_state['recent_memories'] else 'None'}\n"
            f"Long-Term Memory: {self.long_term_memory.get_all_memories() if self.long_term_memory.get_all_memories() else 'None'}\n"
            f"---\n"
            f"User: {user_state['name']}\n"
            f"Relationship with Poppy: {user_state['relationship_with_character']}\n"
            f"Recent Memories (User): {user_state['recent_memories']}"
        )
        logger.info(context)

        return {
            "character_name": char_base['name'],
            "personality": char_base['personality'],
            "location": dyn_state['location'],
            "action": dyn_state['action'],
            "emotional_guidance": emotional_guidance,
            "dynamic_memory": dyn_state['recent_memories'].split(" | ") if dyn_state['recent_memories'] else [],
            "long_term_memory": self.long_term_memory.get_all_memories() if self.long_term_memory.get_all_memories() else [],
            "user_name": user_state['name'],
            "user_input": user_input
        }

    def manage_dynamic_memory(self, user_input, dialogue):
        user_state = self.user_memory.get_user_info()
        event = f"{user_state['name']} said: '{user_input}'. Poppy responded: '{dialogue}'. [Emotional state: {', '.join(self.emotional_core._determine_emotional_state())}]"
        self.dynamic_memory.add_memory(event, self.active_memory)
        self.user_memory.add_memory(f"Poppy said: '{dialogue}'")
