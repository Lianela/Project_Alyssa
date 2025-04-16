# logic.py
import logging
from character_memory import CharacterMemory, UserMemory
from active_memory import ActiveMemoryFile
from emotionalcore import EmotionalCore
# Removed: from dynamic_memory import DynamicMemory - Breaks circular import
from long_term_memory import LongTermMemoryFile

# Set up logging (Consider configuring this centrally if used across modules)
# logging.basicConfig(
#     filename="debug.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(message)s",
#     filemode="a"
# )
logger = logging.getLogger(__name__) # Use __name__ for module-specific logger

class RPLogic:
    # Ensure dynamic_memory is passed in the constructor
    def __init__(self, character_memory, active_memory, user_memory, emotional_core, dynamic_memory):
        self.character_memory = character_memory
        self.active_memory = active_memory
        self.user_memory = user_memory
        self.long_term_memory = LongTermMemoryFile() # Initialize Long Term Memory
        self.dynamic_memory = dynamic_memory # Use the passed-in instance
        self.emotional_core = emotional_core
        self.logger = logger # Assign logger to instance if needed elsewhere

    # Added back from logic_old.py
    def update_location_and_action(self, user_input):
        """Dynamically updates location and action based on keywords in user input."""
        user_input = user_input.lower()
        # Define potential location keywords and their canonical names
        locations = {
            "house": "Poppy's House", "park": "Park", "library": "Library",
            "school": "School", "science class": "Science Class"
        }
        # Define potential action keywords and their canonical action descriptions
        actions = {
            "work": "Working on the project", "continue": "Continuing the project",
            "plan": "Planning the project", "relax": "Relaxing",
            "start": "Starting the project"
        }

        location_updated = False
        for keyword, loc_name in locations.items():
            if keyword in user_input:
                # Use the dynamic_memory instance passed during initialization
                self.dynamic_memory.update_location(loc_name, self.active_memory)
                location_updated = True
                break # Stop after finding the first location keyword

        action_updated = False
        for keyword, act_desc in actions.items():
            if keyword in user_input:
                 # Use the dynamic_memory instance passed during initialization
                self.dynamic_memory.update_action(act_desc, self.active_memory)
                action_updated = True
                break # Stop after finding the first action keyword

        # Log if updates occurred
        if location_updated or action_updated:
            self.logger.info(f"Location/Action updated based on input: '{user_input}'")


    # Added back from logic_old.py
    def construct_context(self, user_input):
        """Constructs the context dictionary needed for the dialogue generator."""
        self.update_location_and_action(user_input) # Update location/action first
        dyn_state = self.dynamic_memory.current_state()
        active_state = self.active_memory.current_state()

        # Determine context flags like location type and recent failure
        context_flags = {
            "location": "public" if dyn_state.get('location', 'Unknown') != "Poppy's House" else "private",
            "recent_failure": any("fail" in mem.lower() for mem in
                                (dyn_state.get('recent_memories', '').split(" | ") +
                                 active_state.get('recent_memories', '').split(" | ")) if mem),
            # Add more context flags as needed
            # Example: Check for high impact event keywords
             "high_impact_event": any(word in user_input.lower() for word in ["die", "death", "gone", "kill", "razor", "cut", "suicide", "depress"])

        }

        # Get emotional guidance from the emotional core
        emotional_guidance = self.emotional_core.process_interaction(user_input, context_flags)

        # Get character and user info
        char_base = self.character_memory.get_character_info()
        user_state = self.user_memory.get_user_info()

        # Construct Internal Thought Log
        internal_thought = (
            f"[INTERNAL THOUGHT]\n"
            f"{char_base.get('name', 'Character')} is in {dyn_state.get('location', 'Unknown')}. "
            f"She is currently {dyn_state.get('action', 'doing something').lower()}. "
            f"Her internal state feels like: {emotional_guidance.get('internal_feeling', 'unknown')}. "
            f"She is expressing: {emotional_guidance.get('expressed_feeling', 'unknown')}. "
            f"Her emotional state is: {', '.join(emotional_guidance.get('emotional_state', ['unknown'])).lower()}. "
            f"Her attitude is: {emotional_guidance.get('attitude', 'unknown').lower()}. "
            f"Her relationship with {user_state.get('name', 'User')} is: {emotional_guidance.get('relationship', 'unknown').lower()}."
        )
        self.logger.info(internal_thought) # Log the internal thought

        # Prepare the context dictionary for the generator
        context_dict = {
            "character_name": char_base.get('name', 'Poppy'),
            "personality": char_base.get('personality', 'Unknown'),
            "location": dyn_state.get('location', 'Unknown'),
            "action": dyn_state.get('action', 'Unknown'),
            "emotional_guidance": emotional_guidance,
            "dynamic_memory": dyn_state.get('recent_memories', '').split(" | ") if dyn_state.get('recent_memories') else [],
            # Fetch combined memories for context
            "active_memory": active_state.get('recent_memories', '').split(" | ") if active_state.get('recent_memories') else [],
            "long_term_memory": self.long_term_memory.get_memories(), # Use get_memories()
            "user_name": user_state.get('name', 'User'),
            "user_input": user_input
        }

        self.logger.info(f"Constructed Context: {context_dict}") # Log the constructed context
        return context_dict

    # Added back from logic_old.py
    def manage_dynamic_memory(self, user_input, dialogue):
        """Manages adding events to dynamic memory after a turn."""
        user_state = self.user_memory.get_user_info()
        char_name = self.character_memory.get_character_info().get('name', 'Character')
        # Determine current emotional state for logging
        current_emotional_state = self.emotional_core._determine_emotional_state() # Access directly if needed

        event = (f"{user_state.get('name', 'User')} said: '{user_input}'. "
                 f"{char_name} responded: '{dialogue}'. "
                 f"[Emotional state: {', '.join(current_emotional_state)}]")

        # Add event to dynamic memory, passing active_memory instance
        self.dynamic_memory.add_memory(event, self.active_memory)
        # Add AI's response to user's memory
        self.user_memory.add_memory(f"{char_name} said: '{dialogue}'")
        self.logger.info(f"Managed dynamic memory for event: {event}")

    # Example method placeholder from the newer logic.py
    def process_input(self, user_input):
        # This method now seems redundant given construct_context and manage_dynamic_memory
        # Decide if you still need it or if its logic is covered elsewhere.
        # If kept, ensure it uses self.dynamic_memory correctly.
        # self.dynamic_memory.add_memory(user_input, self.active_memory)
        self.logger.info(f"Processing input (Placeholder Method): {user_input}")
        return "Response based on logic (Placeholder)"