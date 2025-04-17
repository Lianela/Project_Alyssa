# rp_response.py (Local Ollama Only Version)
import logging
import logging.handlers
import sys
import time
import datetime
import json
import os
import requests # Needed to check Ollama server

# Import logic and component classes
from logic import RPLogic
from active_memory import ActiveMemoryFile
from character_memory import CharacterMemory, UserMemory
from emotionalcore import EmotionalCore
from dynamic_memory import DynamicMemory
# --- START CHANGE: Only import the (renamed) local generator ---
from generator import RPDialogueGenerator # Import the local-only generator class
# --- END CHANGE ---


# --- Advanced Logging Setup ---
# (Logging setup remains the same)
log_formatter_detailed = logging.Formatter('%(asctime)s - %(levelname)-8s - %(name)-15s - %(message)s')
log_formatter_simple = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
main_log_handler = logging.FileHandler("debug.log", mode='a', encoding='utf-8')
main_log_handler.setFormatter(log_formatter_detailed)
main_log_handler.setLevel(logging.INFO)
memory_log_handler = logging.FileHandler("memories_debug.log", mode='a', encoding='utf-8')
memory_log_handler.setFormatter(log_formatter_detailed)
memory_log_handler.setLevel(logging.DEBUG)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
memory_logger = logging.getLogger('memory')
logic_logger = logging.getLogger('logic')
generator_logger = logging.getLogger('generator')
emotional_core_logger = logging.getLogger('emotionalcore')
main_script_logger = logging.getLogger('rp_response')
root_logger.addHandler(main_log_handler)
memory_logger.addHandler(memory_log_handler)
memory_logger.propagate = False
# --- End Advanced Logging Setup ---

# --- Configuration ---
# Ensure this matches the model you have downloaded and want Ollama to use
LOCAL_OLLAMA_MODEL_NAME = "llama3.1:latest" # Specific local model tag
LOCAL_OLLAMA_BASE_URL = "http://localhost:11434" # Default Ollama URL

def main():
    main_script_logger.info("--- Starting main function (Local Ollama Mode) ---")

    # --- Initialization ---
    dialogue_generator = None
    try:
        main_script_logger.info("Initializing components...")
        character = CharacterMemory()
        active = ActiveMemoryFile()
        user = UserMemory()
        user.user_name = "Lin" # Set user name
        emotional_core = EmotionalCore()
        dynamic = DynamicMemory()

        # --- START CHANGE: Directly instantiate Local Generator ---
        # No more choice needed. Check Ollama server first.
        main_script_logger.info(f"Attempting to use LocalGenerator with model: {LOCAL_OLLAMA_MODEL_NAME}")
        try:
             ping_response = requests.get(LOCAL_OLLAMA_BASE_URL, timeout=2)
             ping_response.raise_for_status()
             main_script_logger.info(f"Ollama server responded at {LOCAL_OLLAMA_BASE_URL}.")
             # Instantiate the local generator (assuming class name is RPDialogueGenerator now)
             dialogue_generator = RPDialogueGenerator(
                 model_name=LOCAL_OLLAMA_MODEL_NAME,
                 ollama_base_url=LOCAL_OLLAMA_BASE_URL
             )
        except requests.exceptions.Timeout:
             main_script_logger.error(f"Ollama server connection timed out at {LOCAL_OLLAMA_BASE_URL}.")
             print(f"ERROR: Connection to Ollama timed out at {LOCAL_OLLAMA_BASE_URL}. Is it running and responsive?")
             sys.exit(1)
        except requests.exceptions.ConnectionError:
             main_script_logger.error(f"Ollama server not reachable at {LOCAL_OLLAMA_BASE_URL}. Please ensure Ollama is running.")
             print(f"ERROR: Cannot connect to Ollama at {LOCAL_OLLAMA_BASE_URL}. Please start Ollama and ensure the model '{LOCAL_OLLAMA_MODEL_NAME}' is available (use 'ollama list').")
             sys.exit(1)
        except requests.exceptions.RequestException as req_err:
             main_script_logger.error(f"Error checking Ollama connection: {req_err}", exc_info=True)
             print(f"ERROR: Could not verify Ollama connection. Error: {req_err}")
             sys.exit(1)
        # --- END CHANGE ---

        # Initialize Logic
        logic = RPLogic(
            character_memory=character,
            active_memory=active,
            user_memory=user,
            emotional_core=emotional_core,
            dynamic_memory=dynamic
        )
        main_script_logger.info("Components initialized successfully (state loaded if available).")

    except Exception as e:
        main_script_logger.error(f"Error during component initialization: {e}", exc_info=True)
        print(f"FATAL: Error during initialization. Check debug.log. Error: {e}")
        sys.exit(1)

    # --- Initial Setup ---
    main_script_logger.info("Initial setup check complete (state loaded or defaults used).")

    # --- Roleplay Start ---
    # (opening_text definition and printing remains the same)
    current_location = logic.dynamic_memory.location if hasattr(logic, 'dynamic_memory') else "Unknown Location"
    opening_text = (
        f"*Poppy glances at {user.user_name} across the cluttered desk in the {current_location}, "
        f"her perfectly manicured nails tapping impatiently.*\n"
        f"'Ugh, {user.user_name}, I can't believe you fell asleep at my house yesterday,' "
        f"*she snaps, her voice dripping with irritation.*\n"
        f"'Now we're stuck doing extra work because of you. You're lucky I'm even here to fix this mess. "
        f"So, what's your excuse this time?'"
    )
    try:
        print(opening_text)
        print("\n" + "-"*50 + "\n")
        main_script_logger.info("Printed opening text and separator.")
    except Exception as e:
        main_script_logger.error(f"Error printing opening text/separator: {e}", exc_info=True)
        print("[Error displaying opening text - check console encoding? Continuing anyway...]")


    main_script_logger.info("Entering main interactive loop...")
    # --- Interactive Loop ---
    while True:
        try:
            prompt_message = f"You ({user.user_name}): Enter your message (or type 'image' for image input, 'quit' to exit): "
            user_input = input(prompt_message)
            main_script_logger.debug(f"User input received: {user_input[:100]}...")
        except (EOFError, KeyboardInterrupt) as interrupt_err:
             main_script_logger.warning(f"Input interruption received ({type(interrupt_err).__name__}), attempting to save state before exiting.")
             if 'logic' in locals():
                 logic._save_state()
                 print("\nInput interrupted. State saved (if possible). Ending roleplay.")
             else:
                 print("\nInput interrupted before logic initialized. Cannot save state. Exiting.")
             break

        if user_input.lower() in ["quit", "exit"]:
            main_script_logger.info("Quit command received. Saving state...")
            if 'logic' in locals():
                logic._save_state()
                print("State saved. Roleplay ended. Bye!")
            else:
                print("Exiting before logic initialized. Cannot save state. Bye!")
            break

        image_url = None
        user_text_for_context = user_input

        if user_input.lower() == "image":
            try:
                main_script_logger.info("Handling image input.")
                image_url = input("Enter the image URL: ")
                user_text_about_image = input("Enter your message about the image: ")
                user_text_for_context = user_text_about_image
            except (EOFError, KeyboardInterrupt):
                 main_script_logger.warning("Input cancelled during image prompt.")
                 print("\nInput cancelled. Please try again.")
                 continue

        # --- Generate Response ---
        try:
            main_script_logger.info("Constructing context...")
            if 'logic' not in locals() or 'dialogue_generator' not in locals():
                 main_script_logger.error("Logic or Dialogue Generator not initialized. Cannot proceed.")
                 print("ERROR: Core components not initialized. Exiting.")
                 break

            context = logic.construct_context(user_text_for_context)
            main_script_logger.info("Context constructed.")

            # --- START CHANGE: Log generator type (always Local now) ---
            main_script_logger.info("Generating response using Local generator...")
            # --- END CHANGE ---
            # Use the selected generator instance (which is always the local one now)
            ai_text_to_display, ai_text_for_memory = dialogue_generator.generate_response(context, image_url=image_url)
            main_script_logger.info("Response generated.")

            main_script_logger.info("Managing memory...")
            logic.manage_dynamic_memory(user_input if not image_url else f"{user_text_about_image} [Image: {image_url}]", ai_text_for_memory)
            main_script_logger.info("Memory managed.")

            main_script_logger.info("Printing AI response...")
            try:
                print(f"\n{character.character_name}: {ai_text_to_display}")
                print("\n" + "-"*50 + "\n")
                main_script_logger.info("AI response printed.")
            except Exception as e:
                 main_script_logger.error(f"Error printing AI response: {e}", exc_info=True)
                 print(f"\n[{character.character_name} responded, but there was an error displaying it.]")
                 print("\n" + "-"*50 + "\n")

        except Exception as e:
            main_script_logger.error(f"An error occurred during response generation cycle: {e}", exc_info=True)
            print(f"\n{character.character_name}: *Poppy shrugs.* 'Uh, somethin's busted. Deal with it.'")
            print(f"[Error occurred. Check debug.log. Error: {e}]")
            print("\n" + "-"*50 + "\n")

    main_script_logger.info("--- Exiting main function ---")

if __name__ == "__main__":
    main_script_logger.info("--- Script starting execution ---")
    main()
    main_script_logger.info("--- Script finished ---")

