# logic.py (Option 2 Impl + Detailed Logging + Dynamic Time + Persistence Fixes)
import logging
import re
import time
import datetime
import json # Needed for saving/loading state
import os   # Needed for checking if save file exists

# Get loggers for this module and for memory operations initiated here
logic_logger = logging.getLogger('logic')
# Use a sub-logger of 'memory' for memory actions initiated by logic
memory_logger = logging.getLogger('memory.logic_interface')

SAVE_STATE_FILE = "save_state.json" # Define save file name

class RPLogic:
    def __init__(self, character_memory, active_memory, user_memory, emotional_core, dynamic_memory):
        self.character_memory = character_memory
        self.active_memory = active_memory
        self.user_memory = user_memory
        # Access LTM instance via ActiveMemory's instance
        if hasattr(self.active_memory, 'long_term_file') and self.active_memory.long_term_file:
            self.long_term_memory = self.active_memory.long_term_file
        else:
            logic_logger.error("LongTermMemoryFile instance not found via ActiveMemoryFile. LTM will not function correctly.")
            from long_term_memory import LongTermMemoryFile # Local import for fallback
            self.long_term_memory = LongTermMemoryFile()

        self.dynamic_memory = dynamic_memory
        self.emotional_core = emotional_core
        self.logger = logic_logger
        self.action_regex = re.compile(r"\*(.*?)\*", re.DOTALL)

        # --- Default Initial State ---
        self.current_roleplay_time = datetime.datetime(2025, 4, 16, 14, 0, 0) # Default start time
        self.last_real_time = time.time()
        self.time_scale_factor = 15
        self.min_time_advance_per_turn = datetime.timedelta(minutes=2)

        # --- Attempt to Load Saved State ---
        self._load_state() # Override defaults if save file exists

        self.logger.info("RPLogic initialized. Current roleplay time: %s", self.current_roleplay_time.strftime("%Y-%m-%d %H:%M:%S"))


    # --- START: Save/Load State Methods ---
    def _load_state(self):
        """Loads the roleplay state from the save file if it exists."""
        if os.path.exists(SAVE_STATE_FILE):
            self.logger.info("Save file '%s' found. Attempting to load state.", SAVE_STATE_FILE)
            try:
                with open(SAVE_STATE_FILE, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                self.logger.debug("Loaded raw state data: %s", state_data)

                # Restore Time
                time_str = state_data.get("current_roleplay_time")
                if time_str:
                    try:
                        if '+' in time_str or 'Z' in time_str:
                             self.current_roleplay_time = datetime.datetime.fromisoformat(time_str)
                        else:
                             loaded_time = datetime.datetime.fromisoformat(time_str)
                             self.current_roleplay_time = loaded_time
                        self.logger.info("Loaded roleplay time: %s", self.current_roleplay_time.strftime("%Y-%m-%d %H:%M:%S"))
                    except ValueError as time_err:
                        self.logger.error("Failed to parse saved roleplay time '%s': %s. Using default.", time_str, time_err)

                # Restore Last Action
                last_action = state_data.get("last_narrative_action")
                if last_action is not None:
                    self.dynamic_memory.last_narrative_action = last_action
                    self.logger.info("Loaded last narrative action: %s", last_action)

                # Restore Memories
                self.dynamic_memory.memories = state_data.get("dynamic_memory", [])
                self.active_memory.memories = state_data.get("active_memory", [])
                if self.long_term_memory:
                     self.long_term_memory.memory = state_data.get("long_term_memory", [])
                else:
                     self.logger.warning("LTM object not available during state load for LTM list.")
                self.user_memory.history = state_data.get("user_memory_history", [])
                self.logger.info("Loaded memory lists (Dynamic: %d, Active: %d, LTM: %d, User: %d items).",
                                len(self.dynamic_memory.memories), len(self.active_memory.memories),
                                len(self.long_term_memory.memory) if self.long_term_memory else -1,
                                len(self.user_memory.history))

                # Restore Key Emotional Core Attributes
                emo_state = state_data.get("emotional_core_state", {})
                if emo_state:
                    self.logger.debug("Loading emotional core state attributes: %s", emo_state)
                    # Only load attributes known to exist
                    self.emotional_core.fatigue_level = float(emo_state.get("fatigue_level", self.emotional_core.fatigue_level))
                    self.emotional_core.time_since_last_sleep = float(emo_state.get("time_since_last_sleep", self.emotional_core.time_since_last_sleep))
                    # Removed current_trust and current_intimacy as they caused AttributeErrors
                    self.logger.info("Loaded key emotional state attributes (Fatigue: %.2f, Time Since Sleep: %.1f).",
                                    self.emotional_core.fatigue_level, self.emotional_core.time_since_last_sleep)

                self.last_real_time = time.time()
                self.logger.info("State loaded successfully. Real time tracker reset.")

            except (json.JSONDecodeError, IOError, TypeError, KeyError, AttributeError) as e:
                self.logger.error("Failed to load state from '%s': %s. Starting with default state.", SAVE_STATE_FILE, e, exc_info=True)
        else:
            self.logger.info("No save file '%s' found. Starting with default state.", SAVE_STATE_FILE)

    def _save_state(self):
        """Saves the current roleplay state to the save file."""
        self.logger.info("Attempting to save state to '%s'...", SAVE_STATE_FILE)
        # --- START FIX: Define temp_save_file before try block ---
        temp_save_file = SAVE_STATE_FILE + ".tmp"
        # --- END FIX ---
        try:
            # Ensure LTM object exists before trying to access its memory
            ltm_memory_to_save = self.long_term_memory.memory if self.long_term_memory else []

            # --- START FIX: Remove attributes causing errors ---
            state_data = {
                "current_roleplay_time": self.current_roleplay_time.isoformat(),
                "last_narrative_action": self.dynamic_memory.last_narrative_action,
                "dynamic_memory": self.dynamic_memory.memories,
                "active_memory": self.active_memory.memories,
                "long_term_memory": ltm_memory_to_save,
                "user_memory_history": self.user_memory.history,
                "emotional_core_state": {
                    # Only save attributes known to exist in EmotionalCore
                    "fatigue_level": self.emotional_core.fatigue_level,
                    "time_since_last_sleep": self.emotional_core.time_since_last_sleep,
                    # Removed: "current_trust": self.emotional_core.current_trust,
                    # Removed: "current_intimacy": self.emotional_core.current_intimacy,
                }
            }
            # --- END FIX ---
            self.logger.debug("State data prepared for saving: %s", state_data)

            # Use a temporary file and atomic rename for safer saving
            with open(temp_save_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=4, ensure_ascii=False)

            os.replace(temp_save_file, SAVE_STATE_FILE)

            self.logger.info("State saved successfully to '%s'.", SAVE_STATE_FILE)

        except (IOError, TypeError, AttributeError) as e: # Catch specific expected errors during state gathering/writing
            self.logger.error("Failed to save state to '%s': %s", SAVE_STATE_FILE, e, exc_info=True)
            # Attempt to remove temporary file if save failed
            # Now temp_save_file is guaranteed to be defined here
            if os.path.exists(temp_save_file):
                try:
                    os.remove(temp_save_file)
                    self.logger.info("Removed temporary save file '%s' after error.", temp_save_file)
                except OSError as remove_err:
                     self.logger.error("Failed to remove temporary save file '%s': %s", temp_save_file, remove_err)
        except Exception as e: # Catch any other unexpected error
             self.logger.error("Unexpected error during save state: %s", e, exc_info=True)
             # Also try to remove temp file
             if os.path.exists(temp_save_file):
                try:
                    os.remove(temp_save_file)
                except OSError as remove_err:
                     self.logger.error("Failed to remove temporary save file '%s' after unexpected error: %s", temp_save_file, remove_err)

    # --- END: Save/Load State Methods ---


    def _update_location_and_action_from_input(self, user_input):
        # (Implementation remains the same)
        """Dynamically updates location and general task based on keywords in user input."""
        self.logger.debug("Checking user input for location/action keywords: '%s...'", user_input[:50])
        user_input_lower = user_input.lower()
        locations = { "house": "Poppy's House", "park": "Park", "library": "Library", "school": "School", "science class": "Science Class" }
        actions = { "work": "Working on the project", "continue": "Continuing the project", "plan": "Planning the project", "relax": "Relaxing", "start": "Starting the project" }
        location_updated = False
        action_updated = False
        found_loc = None
        for keyword, loc_name in locations.items():
            if keyword in user_input_lower: found_loc = loc_name; break
        if found_loc and found_loc != self.dynamic_memory.location:
             self.dynamic_memory.update_location(found_loc, self.active_memory); location_updated = True
             self.logger.debug("Found location keyword, updated location via DynamicMemory.")
        found_act = None
        for keyword, act_desc in actions.items():
            if keyword in user_input_lower: found_act = act_desc; break
        if found_act and found_act != self.dynamic_memory.current_action:
             self.dynamic_memory.update_action(found_act, self.active_memory); action_updated = True
             self.logger.debug("Found action keyword, updated action via DynamicMemory.")
        if location_updated or action_updated:
            self.logger.info("Location/Task updated based on input: '%s'", user_input)
        else:
            self.logger.debug("No location/action keywords found or no change needed.")


    def construct_context(self, user_input):
        # (Implementation remains the same)
        """Constructs the context dictionary needed for the dialogue generator."""
        self.logger.debug("--- Logic: construct_context called ---")
        self.logger.debug("User input for context: '%s...'", user_input[:100])

        dyn_state = self.dynamic_memory.current_state()
        active_mems_list = self.active_memory.get_recent_active_memories(count=10)
        ltm_list = self.long_term_memory.get_memories() if self.long_term_memory else []
        user_state = self.user_memory.get_user_info()
        previous_narrative_action = self.dynamic_memory.last_narrative_action
        current_time_str = self.current_roleplay_time.strftime("%A, %I:%M %p")

        self.logger.debug("Dynamic state fetched: %s", dyn_state)
        self.logger.debug("Active memories fetched (count=%d): %s", len(active_mems_list), active_mems_list if len(active_mems_list) < 5 else "[Too many to log fully]")
        self.logger.debug("LTM fetched (count=%d): %s", len(ltm_list), ltm_list if len(ltm_list) < 3 else "[Too many to log fully]")
        self.logger.debug("User state fetched: %s", user_state)
        self.logger.debug("Previous narrative action fetched: %s", previous_narrative_action)
        self.logger.debug("Current roleplay time for context: %s", current_time_str)

        context_flags = {
            "location": "public" if dyn_state.get('location', 'Unknown') not in ["Poppy's House"] else "private",
            "recent_failure": any("fail" in mem.lower() for mem in (dyn_state.get('recent_memories', '').split(" | ") + active_mems_list) if mem),
            "high_impact_event": any(word in user_input.lower() for word in ["die", "death", "gone", "kill", "razor", "cut", "suicide", "depress"])
        }
        self.logger.debug("Context flags determined: %s", context_flags)

        self.logger.debug("Processing interaction with EmotionalCore...")
        emotional_guidance = self.emotional_core.process_interaction(user_input, context_flags)
        self.logger.debug("Emotional guidance received (keys): %s", emotional_guidance.keys())

        char_base = self.character_memory.get_character_info()
        self.logger.debug("Character base info fetched.")

        self.logger.debug("Assembling final context dictionary...")
        context_dict = {
            "character_name": char_base.get('name', 'Poppy'),
            "personality": char_base.get('personality', 'Unknown'),
            "location": dyn_state.get('location', 'Unknown'),
            "action": dyn_state.get('action', 'Unknown'),
            "current_time_in_roleplay": current_time_str,
            "emotional_guidance": emotional_guidance,
            "previous_action": previous_narrative_action,
            "dynamic_memory": dyn_state.get('recent_memories', '').split(" | ") if dyn_state.get('recent_memories') else [],
            "active_memory": active_mems_list,
            "long_term_memory": ltm_list,
            "user_name": user_state.get('name', 'User'),
            "user_input": user_input,
            "user_memories": user_state.get('recent_memories', '').split(" | ") if user_state.get('recent_memories') else []
        }

        self.logger.info("Context constructed successfully.")
        self.logger.debug("--- Logic: construct_context finished ---")
        return context_dict


    def manage_dynamic_memory(self, user_input, full_ai_response):
        # (Implementation remains the same)
        """Manages adding events to memory, updating narrative action,
           updating roleplay time, and updating state AFTER a turn."""
        self.logger.debug("--- Logic: manage_dynamic_memory called ---")
        self.logger.debug("User input: '%s...'", user_input[:100])
        self.logger.debug("Full AI response: '%s...'", full_ai_response[:150])

        # --- Time Advancement Logic ---
        current_real_time = time.time()
        real_delta_seconds = current_real_time - self.last_real_time
        self.logger.debug("Real time delta since last turn: %.2f seconds", real_delta_seconds)
        self.last_real_time = current_real_time
        roleplay_delta_scaled = datetime.timedelta(seconds=real_delta_seconds * self.time_scale_factor)
        roleplay_delta = max(roleplay_delta_scaled, self.min_time_advance_per_turn)
        self.logger.debug("Calculated roleplay time delta (scaled): %s", roleplay_delta_scaled)
        self.logger.debug("Minimum time advance per turn: %s", self.min_time_advance_per_turn)
        self.logger.debug("Final roleplay time delta to apply: %s", roleplay_delta)
        self.current_roleplay_time += roleplay_delta
        self.logger.info("Roleplay time advanced to: %s", self.current_roleplay_time.strftime("%Y-%m-%d %H:%M:%S"))
        # --- End Time Advancement ---

        user_state = self.user_memory.get_user_info()
        char_name = self.character_memory.get_character_info().get('name', 'Character')
        current_emotional_state = self.emotional_core.emotional_state_labels
        self.logger.debug("Current emotional state labels for event: %s", current_emotional_state)

        # 1. Construct the event string
        event = (f"{user_state.get('name', 'User')} said: '{user_input}'. "
                 f"{char_name} responded: '{full_ai_response}'. "
                 f"[Emotional state: {', '.join(current_emotional_state)}]")
        self.logger.debug("Constructed event string: '%s...'", event[:200])

        # 2. Add event to dynamic memory
        self.logger.debug("Calling dynamic_memory.add_memory...")
        self.dynamic_memory.add_memory(event, self.active_memory)

        # 3. Add AI's response to user's memory
        user_memory_entry = f"{char_name} said: '{full_ai_response}'"
        self.logger.debug("Adding to user_memory: '%s...'", user_memory_entry[:100])
        self.user_memory.add_memory(user_memory_entry)

        # 4. Extract and store last narrative action
        self.logger.debug("Attempting to extract narrative action from response...")
        extracted_action = "*[Action could not be parsed]*"
        match = self.action_regex.search(full_ai_response)
        if match:
            extracted_action = f"*{match.group(1).strip()}*"
            self.logger.debug("Action extracted using regex: %s", extracted_action)
        else:
             lines = full_ai_response.split('\n', 1)
             first_line = lines[0].strip()
             if len(first_line) < 150 and first_line.startswith("*") and first_line.endswith("*"):
                  extracted_action = first_line
                  self.logger.warning("Could not find action reliably with regex, using first line wrapped in '*': %s", extracted_action)
             else:
                  self.logger.warning("Could not parse narrative action from response: '%s...'", full_ai_response[:100])

        memory_logger.debug("Setting last narrative action in DynamicMemory: %s", extracted_action)
        self.dynamic_memory.set_last_narrative_action(extracted_action)

        # 5. Update location/general task based on the user_input from this turn
        self.logger.debug("Calling _update_location_and_action_from_input...")
        self._update_location_and_action_from_input(user_input)

        self.logger.info("Memory managed for turn.")
        self.logger.debug("--- Logic: manage_dynamic_memory finished ---")

