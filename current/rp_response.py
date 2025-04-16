# rp_response.py
import logging # Import logging if you want to configure it here
from logic import RPLogic
from generator import RPDialogueGenerator
from active_memory import ActiveMemoryFile
from character_memory import CharacterMemory, UserMemory
from emotionalcore import EmotionalCore
from dynamic_memory import DynamicMemory

# Optional: Configure logging centrally
# logging.basicConfig(filename='rp_app.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w')

def main():
    # --- Initialization ---
    character = CharacterMemory()
    active = ActiveMemoryFile() # Thresholds can be adjusted
    user = UserMemory()
    user.user_name = "Lin" # Set user name
    emotional_core = EmotionalCore()
    dynamic = DynamicMemory() # Initialize Dynamic Memory

    # Initialize RPLogic, passing all required components
    logic = RPLogic(
        character_memory=character,
        active_memory=active,
        user_memory=user,
        emotional_core=emotional_core,
        dynamic_memory=dynamic # Pass the dynamic memory instance
    )
    dialogue_generator = RPDialogueGenerator()

    # --- Initial Setup ---
    # Initialize Dynamic Memory with starting situation via logic instance
    logic.dynamic_memory.update_location("School Library", logic.active_memory) # More specific location
    logic.dynamic_memory.update_action("waiting to discuss the project", logic.active_memory)

    # Add initial event establishing the backstory/premise
    initial_event = "Lin fell asleep yesterday instead of finishing the project work with Poppy. Poppy called but got no response."
    logic.dynamic_memory.add_memory(initial_event, logic.active_memory)
    logging.info(f"Initial event added: {initial_event}")

    # --- Roleplay Start ---
    opening_text = (
        f"*Poppy glances at {user.user_name} across the cluttered desk in the School Library, "
        f"her perfectly manicured nails tapping impatiently.*\n"
        f"'Ugh, {user.user_name}, I can’t believe you fell asleep at my house yesterday,' "
        f"*she snaps, her voice dripping with irritation.*\n"
        f"'Now we’re stuck doing extra work because of you. You’re lucky I’m even here to fix this mess. "
        f"So, what’s your excuse this time?'"
    )
    print(opening_text)
    print("\n" + "-"*50 + "\n")

    # --- Interactive Loop ---
    while True:
        prompt_message = f"You ({user.user_name}): Enter your message (or type 'image' for image input, 'quit' to exit): "
        user_input = input(prompt_message)

        if user_input.lower() in ["quit", "exit"]:
            print("Roleplay ended. Bye!")
            break

        image_url = None
        user_text_for_context = user_input # Default to user input

        if user_input.lower() == "image":
            try:
                image_url = input("Enter the image URL: ")
                user_text_about_image = input("Enter your message about the image: ")
                user_text_for_context = user_text_about_image # Use image description for context
                print("\n" + "-"*50 + "\n")
            except EOFError: # Handle potential input errors gracefully
                 print("\nInput cancelled. Please try again.")
                 continue

        else: # Regular text input
            print("\n" + "-"*50 + "\n")

        # --- Generate Response ---
        try:
            # 1. Construct context using the logic module
            context = logic.construct_context(user_text_for_context)

            # 2. Generate AI response using the generator
            ai_text, dialogue = dialogue_generator.generate_response(context, image_url=image_url)

            # 3. Manage memory after the turn
            # Pass the original user input (even if image related) and the generated dialogue
            logic.manage_dynamic_memory(user_input if not image_url else f"{user_text_about_image} [Image: {image_url}]", dialogue)

            # 4. Print AI response
            print(f"{character.character_name}: {ai_text}")

        except Exception as e:
            logging.error(f"An error occurred during response generation: {e}", exc_info=True)
            print("Sorry, something went wrong on my end. Let's try that again.") # User-friendly error

        print("\n" + "-"*50 + "\n")


if __name__ == "__main__":
    main()