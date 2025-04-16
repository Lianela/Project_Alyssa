# rp_response.py
from logic import RPLogic
from generator import RPDialogueGenerator
from active_memory import ActiveMemoryFile
from character_memory import CharacterMemory, UserMemory
from emotionalcore import EmotionalCore
from dynamic_memory import DynamicMemory

def main():
    character = CharacterMemory()
    active = ActiveMemoryFile()
    user = UserMemory()
    user.user_name = "Lin"
    emotional_core = EmotionalCore()
    dynamic = DynamicMemory()
    logic = RPLogic(character, active, user, emotional_core, dynamic)
    dialogue_generator = RPDialogueGenerator()

    # Initialize Dynamic Memory with starting situation
    logic.dynamic_memory.update_location("School", logic.active_memory)
    logic.dynamic_memory.update_action("Doing the project with Lin", logic.active_memory)

    # Add initial Dynamic Memory event
    logic.dynamic_memory.add_memory("Lin fell asleep yesterday instead of doing the homework with Poppy, Poppy also called her but got no response so wasn't able to do it.", logic.active_memory)

    # Default roleplay opening text
    opening_text = (
        "*Poppy glances at Lin across the cluttered desk in the School library, her perfectly manicured nails tapping impatiently.*\n"
        "'Ugh, Lin, I can’t believe you fell asleep at my house yesterday,' *she snaps, her voice dripping with irritation.*\n"
        "'Now we’re stuck doing extra work because of you. You’re lucky I’m even here to fix this mess. So, what’s your excuse this time?'"
    )
    print(opening_text)
    print("\n" + "-"*50 + "\n")

    # Interactive loop with support for image input
    while True:
        print("You (Lin): Enter your message (or type 'image' to provide an image URL, or 'quit' to exit):")
        user_input = input("You (Lin): ")
        if user_input.lower() in ["quit", "exit"]:
            print("Roleplay ended. Bye!")
            break
        if user_input.lower() == "image":
            image_url = input("Enter the image URL: ")
            user_text = input("Enter your message about the image: ")
            print("\n" + "-"*50 + "\n")
            context = logic.construct_context(user_text)
            ai_text, dialogue = dialogue_generator.generate_response(context, image_url=image_url)
            logic.manage_dynamic_memory(user_text, dialogue)
            print(ai_text)
        else:
            print("\n" + "-"*50 + "\n")
            context = logic.construct_context(user_input)
            ai_text, dialogue = dialogue_generator.generate_response(context)
            logic.manage_dynamic_memory(user_input, dialogue)
            print(ai_text)
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()