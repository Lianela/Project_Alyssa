# rp_response.py
import logging
import logging.handlers # Needed for different handlers if desired
import sys
# Import other necessary modules
from logic import RPLogic
from generator import RPDialogueGenerator
from active_memory import ActiveMemoryFile
from character_memory import CharacterMemory, UserMemory
from emotionalcore import EmotionalCore
from dynamic_memory import DynamicMemory

# --- Advanced Logging Setup ---
# Define log formats
log_formatter_detailed = logging.Formatter(
    '%(asctime)s - %(levelname)-8s - %(name)-15s - %(message)s' # Include logger name
)
log_formatter_simple = logging.Formatter(
    '%(asctime)s - %(levelname)-8s - %(message)s'
)

# ---- Main Debug Log Handler (debug.log) ----
main_log_handler = logging.FileHandler("debug.log", mode='a', encoding='utf-8')
main_log_handler.setFormatter(log_formatter_detailed)
main_log_handler.setLevel(logging.INFO) # Log INFO and above for general flow/errors

# ---- Memory Debug Log Handler (memories_debug.log) ----
memory_log_handler = logging.FileHandler("memories_debug.log", mode='a', encoding='utf-8')
memory_log_handler.setFormatter(log_formatter_detailed) # Use detailed format here too
memory_log_handler.setLevel(logging.DEBUG) # Log EVERYTHING (DEBUG and above) for memories

# ---- Get Loggers ----
# Get the root logger - catches everything by default
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG) # Set root logger to lowest level to allow handlers to filter

# Get specific loggers for different parts of the application
memory_logger = logging.getLogger('memory') # Logger for all memory modules (and its children like memory.dynamic)
logic_logger = logging.getLogger('logic')
generator_logger = logging.getLogger('generator')
emotional_core_logger = logging.getLogger('emotionalcore')
main_script_logger = logging.getLogger('rp_response') # Logger for this main script

# ---- Assign Handlers ----
# Add the main handler to the root logger. Logs from any logger
# set to INFO or higher will go to debug.log, unless propagation is disabled.
root_logger.addHandler(main_log_handler)

# Add the memory handler ONLY to the memory logger.
# Only logs from getLogger('memory') or its children (e.g., 'memory.dynamic')
# set to DEBUG or higher will go to memories_debug.log.
memory_logger.addHandler(memory_log_handler)
memory_logger.propagate = False # IMPORTANT: Prevent memory logs from also going to debug.log via root

# --- End Advanced Logging Setup ---

def main():
    main_script_logger.info("--- Starting main function ---")
    # --- Initialization ---
    try:
        main_script_logger.info("Initializing components...")
        character = CharacterMemory()
        active = ActiveMemoryFile() # Thresholds can be adjusted
        user = UserMemory()
        user.user_name = "Lin" # Set user name
        # Ensure EmotionalCore() initialization doesn't error out silently
        emotional_core = EmotionalCore()
        dynamic = DynamicMemory() # Initialize Dynamic Memory

        # Ensure RPLogic() initialization doesn't error out silently
        logic = RPLogic(
            character_memory=character,
            active_memory=active,
            user_memory=user,
            emotional_core=emotional_core,
            dynamic_memory=dynamic
        )
        # Ensure RPDialogueGenerator() initialization doesn't error out silently
        dialogue_generator = RPDialogueGenerator()
        main_script_logger.info("Components initialized successfully.")
    except Exception as e:
        main_script_logger.error(f"Error during component initialization: {e}", exc_info=True)
        # Also print to console as logging might fail if it happens early
        print(f"FATAL: Error during initialization. Check debug.log. Error: {e}")
        sys.exit(1) # Exit if initialization fails

    # --- Initial Setup ---
    try:
        main_script_logger.info("Performing initial setup...")
        # The actual logging for these actions should happen inside the methods if needed
        logic.dynamic_memory.update_location("School Library", logic.active_memory)
        logic.dynamic_memory.update_action("waiting to discuss the project", logic.active_memory)

        initial_event = "Lin fell asleep yesterday instead of finishing the project work with Poppy. Poppy called but got no response."
        # The logic.dynamic_memory.add_memory call will trigger logs via the 'memory.dynamic' logger
        logic.dynamic_memory.add_memory(initial_event, logic.active_memory)
        main_script_logger.info("Initial setup complete.")
    except Exception as e:
        main_script_logger.error(f"Error during initial setup: {e}", exc_info=True)
        print(f"FATAL: Error during setup. Check debug.log. Error: {e}")
        sys.exit(1)

    # --- Roleplay Start ---
    opening_text = (
        f"*Poppy glances at {user.user_name} across the cluttered desk in the School Library, "
        f"her perfectly manicured nails tapping impatiently.*\n"
        # Using standard single quotes (') instead of smart quotes (’ / ‘)
        f"'Ugh, {user.user_name}, I can't believe you fell asleep at my house yesterday,' "
        f"*she snaps, her voice dripping with irritation.*\n"
        f"'Now we're stuck doing extra work because of you. You're lucky I'm even here to fix this mess. "
        f"So, what's your excuse this time?'"
    )

    # Print opening text (uncommented as requested, watch for encoding errors)
    try:
        print(opening_text)
        print("\n" + "-"*50 + "\n")
        main_script_logger.info("Printed opening text and separator.")
    except Exception as e:
        # If printing fails, log it and try to continue
        main_script_logger.error(f"Error printing opening text/separator: {e}", exc_info=True)
        print("[Error displaying opening text - check console encoding? Continuing anyway...]")

    main_script_logger.info("Entering main interactive loop...")
    # --- Interactive Loop ---
    while True:
        try: # Added try block around input for robustness
            prompt_message = f"You ({user.user_name}): Enter your message (or type 'image' for image input, 'quit' to exit): "
            user_input = input(prompt_message)
            main_script_logger.debug(f"User input received: {user_input[:100]}...") # Log input
        except EOFError:
            main_script_logger.warning("EOFError received on input, ending roleplay.")
            print("\nInput stream closed. Ending roleplay.")
            break
        except KeyboardInterrupt:
            main_script_logger.warning("KeyboardInterrupt received, ending roleplay.")
            print("\nRoleplay interrupted by user. Bye!")
            break

        if user_input.lower() in ["quit", "exit"]:
            main_script_logger.info("Quit command received. Ending roleplay.")
            print("Roleplay ended. Bye!")
            break

        image_url = None
        user_text_for_context = user_input # Default to user input

        if user_input.lower() == "image":
            try:
                main_script_logger.info("Handling image input.")
                image_url = input("Enter the image URL: ")
                user_text_about_image = input("Enter your message about the image: ")
                user_text_for_context = user_text_about_image # Use image description for context
            except (EOFError, KeyboardInterrupt):
                 main_script_logger.warning("Input cancelled during image prompt.")
                 print("\nInput cancelled. Please try again.")
                 continue

        # --- Generate Response ---
        try:
            main_script_logger.info("Constructing context...")
            context = logic.construct_context(user_text_for_context)
            main_script_logger.info("Context constructed.")

            main_script_logger.info("Generating response...")
            # generate_response internal logs will use 'generator' logger
            ai_text_to_display, ai_text_for_memory = dialogue_generator.generate_response(context, image_url=image_url)
            main_script_logger.info("Response generated.")

            main_script_logger.info("Managing memory...")
            # manage_dynamic_memory internal logs will use 'logic' and 'memory.*' loggers
            logic.manage_dynamic_memory(user_input if not image_url else f"{user_text_about_image} [Image: {image_url}]", ai_text_for_memory)
            main_script_logger.info("Memory managed.")

            main_script_logger.info("Printing AI response...")
            try:
                # Print the combined action + dialogue
                print(f"\n{character.character_name}: {ai_text_to_display}")
                print("\n" + "-"*50 + "\n") # Print separator after AI response
                main_script_logger.info("AI response printed.")
            except Exception as e:
                 main_script_logger.error(f"Error printing AI response: {e}", exc_info=True)
                 print(f"\n[{character.character_name} responded, but there was an error displaying it.]")
                 print("\n" + "-"*50 + "\n")

        except Exception as e:
            # Catch errors during context, generation, or memory management
            main_script_logger.error(f"An error occurred during response generation cycle: {e}", exc_info=True)
            # Using standard single quote (') for potentially problematic character (’)
            print(f"\n{character.character_name}: *Poppy shrugs.* 'Uh, somethin's busted. Deal with it.'")
            print(f"[Error occurred. Check debug.log. Error: {e}]") # Inform user
            print("\n" + "-"*50 + "\n")

    main_script_logger.info("--- Exiting main function ---")

if __name__ == "__main__":
    # Logging is configured above when the module is loaded.
    # We can just log that the script is starting execution.
    main_script_logger.info("--- Script starting execution ---")
    # print("DEBUG: Script starting...") # Console print optional
    main()
    # print("DEBUG: Script finished.") # Console print optional
    main_script_logger.info("--- Script finished ---")

