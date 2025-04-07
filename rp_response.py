import openai
import logging
from active_memory import ActiveMemoryFile
from character_memory import CharacterMemory, UserMemory
from long_term_memory import LongTermMemoryFile

# Set up logging to a file for debug info
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filemode="a"  # Append mode
)
logger = logging.getLogger()

class RPLogic:
    def __init__(self, character_memory, active_memory, user_memory):
        self.character_memory = character_memory
        self.active_memory = active_memory
        self.user_memory = user_memory
        self.long_term_memory = LongTermMemoryFile()  # Long-Term Memory
        self.dynamic_memory = []  # Dynamic Memory list
        self.dynamic_memory_limit = 5  # Compress at 5 entries

    def update_location(self, location):
        self.active_memory.update_location(location)

    def update_action(self, action):
        self.active_memory.update_action(action)

    def update_state(self, state):
        self.active_memory.state = state
        self.active_memory.add_memory(f"Feeling {state.lower()}.")

    def parse_user_input(self, user_input):
        """Parse user input to detect changes in location, action, or state."""
        user_input = user_input.lower()

        # Detect location changes
        locations = {
            "house": "Poppy's House",
            "park": "Park",
            "library": "Library",
            "school": "School",
            "science class": "Science Class"
        }
        for keyword, location in locations.items():
            if keyword in user_input:
                self.update_location(location)
                break

        # Detect action changes
        actions = {
            "work": "Working on the project",
            "continue": "Continuing the project",
            "plan": "Planning the project",
            "relax": "Relaxing",
            "start": "Starting the project"
        }
        for keyword, action in actions.items():
            if keyword in user_input:
                self.update_action(action)
                break

        # Detect state changes
        states = {
            "sorry": "Calm",
            "calm": "Calm",
            "angry": "Angry",
            "annoyed": "Annoyed",
            "happy": "Happy",
            "trust": "Trusting"
        }
        for keyword, state in states.items():
            if keyword in user_input:
                self.update_state(state)
                break

    def update_relationship(self, user_input):
        user_input = user_input.lower()
        if "help" in user_input or "please" in user_input:
            self.character_memory.update_relationship("Warming up. Less rivalry.")
            self.user_memory.update_relationship("Growing closer to Poppy.")
        elif "stupid" in user_input or "hate" in user_input:
            self.character_memory.update_relationship("Hostile. Open rivalry.")
            self.user_memory.update_relationship("Tense with Poppy.")
        elif "thanks" in user_input or "cool" in user_input:
            self.character_memory.update_relationship("Reluctant respect. Curiosity growing.")
            self.user_memory.update_relationship("Appreciating Poppy.")

    def manage_dynamic_memory(self, user_input, dialogue):
        user_state = self.user_memory.get_user_info()
        # Add new event to Dynamic Memory
        event = f"{user_state['name']} said: '{user_input}'. Poppy responded: '{dialogue}'."
        self.dynamic_memory.append(event)

        # If Dynamic Memory hits the limit, compress and move to Long-Term
        if len(self.dynamic_memory) >= self.dynamic_memory_limit:
            # Compress: Summarize the events
            summary = f"Poppy interacted with {user_state['name']} over {len(self.dynamic_memory)} events. "
            summary += f"Key themes: {self.character_memory.get_character_info()['relationship_with_user'].lower()}."
            self.long_term_memory.store([summary])  # Store as a list to match LongTermMemoryFile
            self.dynamic_memory = []  # Clear Dynamic Memory after compression

        # Update user memory (Lin's perspective)
        self.user_memory.add_memory(f"Poppy said: '{dialogue}'")

    def generate_thought_and_action(self, user_input):
        char_base = self.character_memory.get_character_info()
        dyn_state = self.active_memory.current_state()
        state = getattr(self.active_memory, 'state', 'neutral')  # Default to 'neutral' if not set
        internal_thought = (
            f"[INTERNAL THOUGHT]\n{char_base['name']} remembers she's in {dyn_state['location']}. "
            f"She is currently {dyn_state['action'].lower()}. Her current state is: {state.lower()}.\n"
            f"Her relationship with {self.user_memory.user_name} is: {char_base['relationship_with_user'].lower()}."
        )
        return internal_thought

    def construct_prompt(self, user_input):
        """Construct the prompt with all relevant context for the dialogue generator."""
        self.parse_user_input(user_input)
        self.update_relationship(user_input)

        char_base = self.character_memory.get_character_info()
        dyn_state = self.active_memory.current_state()
        user_state = self.user_memory.get_user_info()
        state = getattr(self.active_memory, 'state', 'neutral')

        # Log internal thought
        internal_thought = self.generate_thought_and_action(user_input)
        logger.info(internal_thought)

        # Log context
        context = (
            f"Character: {char_base['name']}\n"
            f"Personality: {char_base['personality']}\n"
            f"Active Memory: Location: {dyn_state['location']} | Action: {dyn_state['action']} | State: {state}\n"
            f"Relationship with {user_state['name']}: {char_base['relationship_with_user']}\n"
            f"Dynamic Memory (Recent Events): {self.dynamic_memory[-5:] if self.dynamic_memory else 'None'}\n"
            f"Long-Term Memory: {self.long_term_memory.get_all_memories() if self.long_term_memory.get_all_memories() else 'None'}\n"
            f"---\n"
            f"User: {user_state['name']}\n"
            f"Relationship with Poppy: {user_state['relationship_with_character']}\n"
            f"Recent Memories (User): {user_state['recent_memories']}"
        )
        logger.info(context)

        # Construct the prompt
        prompt = (
            f"You are Poppy, a 21-year-old college student known as the queen of the school. "
            f"Your personality is arrogant, popular, and snarky—you think you’re better than everyone and hide vulnerability under a confident mask. "
            f"You’re currently in {dyn_state['location']}, {dyn_state['action']}. Your current state is {state}. "
            f"Your relationship with {user_state['name']} is {char_base['relationship_with_user']}. "
            f"Recent events: {self.dynamic_memory[-5:] if self.dynamic_memory else 'None'}. "
            f"Long-term memories: {self.long_term_memory.get_all_memories() if self.long_term_memory.get_all_memories() else 'None'}. "
            f"{user_state['name']} just said: '{user_input}'. Respond as Poppy, keeping your tone and personality consistent, and include a short action description in asterisks before your dialogue. "
            f"Avoid repeating phrases or actions from recent responses to keep the dialogue fresh."
        )

        return prompt, user_state['name']

class RPDialogueGenerator:
    def __init__(self):
        # Configure OpenAI SDK for OpenRouter
        openai.api_base = "https://openrouter.ai/api/v1"
        openai.api_key = "YOUR-OPENROUTER-API-KEY"
        logger.info(f"DEBUG: API Key = '{openai.api_key}'")

    def generate_response(self, prompt, user_name, image_url=None):
        """Generate a response for the user, ensuring it feels fresh and consistent with Poppy's character."""
        # Prepare the messages array
        messages = [
            {
                "role": "system",
                "content": "You are Poppy, follow the prompt instructions."
            }
        ]

        # If an image URL is provided, include it in the user message
        if image_url:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": prompt
            })

        # Headers for OpenRouter rankings
        headers = {
            "HTTP-Referer": "http://localhost",
            "X-Title": "PoppyBot"
        }

        try:
            logger.info(f"DEBUG: Headers = {headers}")
            logger.info(f"DEBUG: Sending messages = {messages}")
            response = openai.ChatCompletion.create(
                model="meta-llama/llama-4-maverick:free",
                messages=messages,
                max_tokens=250,
                temperature=0.7,
                headers=headers
            )
            ai_text = response.choices[0].message['content'].strip()
            logger.info(f"DEBUG: Response = {response}")
        except Exception as e:
            ai_text = f"*Poppy shrugs.* 'Uh, somethin’s busted, {user_name}. Deal with it.'"
            logger.info(f"API Error: {str(e)}")

        # Extract dialogue for memory storage
        dialogue = ai_text
        if '*' in ai_text and "'" in ai_text:
            try:
                dialogue = ai_text.split("'", 1)[1].rsplit("'", 1)[0].strip()
            except IndexError:
                pass

        return ai_text, dialogue

if __name__ == "__main__":
    character = CharacterMemory()
    active = ActiveMemoryFile()
    user = UserMemory()
    user.user_name = "Lin"  # Update user name to Lin
    logic = RPLogic(character, active, user)
    dialogue_generator = RPDialogueGenerator()

    # Initialize Active Memory with starting situation
    logic.update_location("School")
    logic.update_action("Doing the project with Lin")
    logic.update_state("Annoyed")

    # Add initial Dynamic Memory event
    logic.dynamic_memory.append("Lin fell asleep yesterday instead of doing the homework with Poppy, Poppy also called her but got no response so wasn't able to do it.")

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
            # Construct prompt and generate response
            prompt, user_name = logic.construct_prompt(user_text)
            ai_text, dialogue = dialogue_generator.generate_response(prompt, user_name, image_url=image_url)
            logic.manage_dynamic_memory(user_text, dialogue)
            print(ai_text)
        else:
            print("\n" + "-"*50 + "\n")
            # Construct prompt and generate response
            prompt, user_name = logic.construct_prompt(user_input)
            ai_text, dialogue = dialogue_generator.generate_response(prompt, user_name)
            logic.manage_dynamic_memory(user_input, dialogue)
            print(ai_text)
        print("\n" + "-"*50 + "\n")
