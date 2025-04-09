import logging
from active_memory import ActiveMemoryFile
from character_memory import CharacterMemory, UserMemory
from long_term_memory import LongTermMemoryFile
from textblob import TextBlob  # For basic sentiment analysis

# Set up logging
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filemode="a"
)
logger = logging.getLogger()

class RPLogic:
    def __init__(self, character_memory, active_memory, user_memory):
        self.character_memory = character_memory
        self.active_memory = active_memory
        self.user_memory = user_memory
        self.long_term_memory = LongTermMemoryFile()
        self.dynamic_memory = []
        self.dynamic_memory_limit = 5
        # Emotional states Poppy can be in
        self.emotional_states = [
            "Calm", "Upset", "Angry", "Anxious", "Reassured", "Vulnerable", "Defensive", "Open"
        ]
        # Initial emotional state
        self.active_memory.state = "Calm"
        # Initial attitude (facade up by default)
        self.attitude = "Facade Up"  # Options: "Facade Up", "Facade Down", "Guarded", "Open"
        # Initial relationship level
        self.relationship_level = "Hostile"  # Options: "Hostile", "Neutral", "Warming Up", "Friendly", "Close"

    def analyze_sentiment(self, text):
        """Analyze the sentiment of a piece of text to determine emotional intent."""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
        if polarity > 0.3:
            return "Positive"
        elif polarity < -0.3:
            return "Negative"
        else:
            return "Neutral"

    def detect_contextual_cues(self, user_input):
        """Detect contextual cues in user input to infer intent (e.g., empathy, aggression)."""
        user_input = user_input.lower()
        cues = {
            "empathy": any(word in user_input for word in ["sorry", "care", "love", "understand", "here for you"]),
            "aggression": any(word in user_input for word in ["hate", "stupid", "annoying", "shut up"]),
            "physical_action": any(word in user_input for word in ["hug", "touch", "hold"]),
            "emotional_observation": any(word in user_input for word in ["sad", "tears", "angry", "hurt"])
        }
        return cues

    def update_location_and_action(self, user_input):
        """Update location and action based on context (simplified for now)."""
        user_input = user_input.lower()
        locations = ["house", "park", "library", "school", "science class"]
        actions = ["work", "continue", "plan", "relax", "start"]
        for loc in locations:
            if loc in user_input:
                self.active_memory.update_location(loc.capitalize() if loc != "house" else "Poppy's House")
                break
        for act in actions:
            if act in user_input:
                self.active_memory.update_action(f"{act.capitalize()}ing the project")
                break

    def update_emotional_state(self, user_input):
        """Dynamically update Poppy's emotional state based on context."""
        # Analyze user input sentiment
        user_sentiment = self.analyze_sentiment(user_input)
        cues = self.detect_contextual_cues(user_input)

        # Analyze recent interactions for patterns
        recent_interactions = self.dynamic_memory[-3:] if len(self.dynamic_memory) >= 3 else self.dynamic_memory
        past_sentiments = [self.analyze_sentiment(event) for event in recent_interactions]
        past_hugs = sum(1 for event in recent_interactions if "hug" in event.lower())
        past_tears = sum(1 for event in recent_interactions if "tears" in event.lower())

        current_state = self.active_memory.state
        location = self.active_memory.current_state()['location']

        # Base state transitions on context
        if cues["physical_action"] and "Poppy's House" in location:
            # Hugs in a safe place (Poppy's House) make her anxious but reassured
            if past_hugs > 1:
                self.active_memory.state = "Reassured"  # Repeated hugs start to feel comforting
            else:
                self.active_memory.state = "Anxious"  # First hug makes her anxious
        elif cues["empathy"] and user_sentiment == "Positive":
            # Empathy and positive sentiment make her feel vulnerable or open
            if current_state in ["Anxious", "Upset"]:
                self.active_memory.state = "Vulnerable"
            elif past_tears > 0:
                self.active_memory.state = "Open"
            else:
                self.active_memory.state = "Calm"
        elif cues["aggression"] or user_sentiment == "Negative":
            # Aggression or negativity makes her defensive or angry
            self.active_memory.state = "Defensive" if current_state != "Angry" else "Angry"
        elif past_tears > 0 and cues["emotional_observation"]:
            # Noticing her tears makes her feel exposed
            self.active_memory.state = "Upset"
        else:
            # Default to calming down if no strong triggers
            self.active_memory.state = "Calm"

        logger.info(f"DEBUG: Emotional state updated to '{self.active_memory.state}'.")

    def update_attitude(self):
        """Adjust Poppy's attitude based on her emotional state and relationship."""
        current_state = self.active_memory.state
        if current_state in ["Angry", "Defensive", "Upset"]:
            self.attitude = "Facade Up"  # Defensive states reinforce her facade
        elif current_state in ["Vulnerable", "Open"]:
            self.attitude = "Facade Down"  # Vulnerable states lower her facade
        elif current_state == "Anxious":
            self.attitude = "Guarded"  # Anxious but in a safe place, she’s hesitant
        elif current_state == "Reassured":
            self.attitude = "Open"  # Reassured, she’s more open to connection
        else:
            self.attitude = "Facade Up"  # Default to facade up when calm

        logger.info(f"DEBUG: Attitude updated to '{self.attitude}'.")

    def update_relationship(self, user_input):
        """Dynamically update the relationship based on context and sentiment."""
        user_sentiment = self.analyze_sentiment(user_input)
        cues = self.detect_contextual_cues(user_input)
        past_interactions = self.long_term_memory.get_all_memories()
        past_relationships = [mem.split("Key themes: ")[1] for mem in past_interactions if "Key themes" in mem]

        # Determine relationship progression
        if cues["empathy"] and user_sentiment == "Positive":
            if "hostile" in past_relationships[-1] if past_relationships else False:
                self.relationship_level = "Warming Up"
            elif "warming up" in past_relationships[-1] if past_relationships else False:
                self.relationship_level = "Friendly"
            else:
                self.relationship_level = "Close"
        elif cues["aggression"] or user_sentiment == "Negative":
            self.relationship_level = "Hostile"
        else:
            self.relationship_level = "Neutral" if not past_relationships else past_relationships[-1].split('.')[0]

        self.character_memory.update_relationship(self.relationship_level)
        self.user_memory.update_relationship(f"Relationship with Poppy: {self.relationship_level}.")
        logger.info(f"DEBUG: Relationship updated to '{self.relationship_level}'.")

    def manage_dynamic_memory(self, user_input, dialogue):
        """Manage Dynamic Memory and compress to Long-Term Memory when needed."""
        user_state = self.user_memory.get_user_info()
        event = f"{user_state['name']} said: '{user_input}'. Poppy responded: '{dialogue}'. [Emotional state: {self.active_memory.state}]"
        self.dynamic_memory.append(event)

        if len(self.dynamic_memory) >= self.dynamic_memory_limit:
            summary = f"Poppy interacted with {user_state['name']} over {len(self.dynamic_memory)} events. "
            summary += f"Key themes: {self.relationship_level.lower()}."
            significant_events = [event for event in self.dynamic_memory if "hug" in event.lower() or "tears" in event.lower()]
            if significant_events:
                summary += f" Significant moments: {'; '.join([event.split('Poppy responded:')[0] for event in significant_events[:2]])}."
            summary += f" Poppy's emotional state at the end: {self.active_memory.state.lower()}."
            self.long_term_memory.store([summary])
            self.dynamic_memory = []

        self.user_memory.add_memory(f"Poppy said: '{dialogue}'")

    def construct_context(self, user_input):
        """Construct the context for the dialogue generator."""
        self.update_location_and_action(user_input)
        self.update_emotional_state(user_input)
        self.update_attitude()
        self.update_relationship(user_input)

        char_base = self.character_memory.get_character_info()
        dyn_state = self.active_memory.current_state()
        user_state = self.user_memory.get_user_info()

        internal_thought = (
            f"[INTERNAL THOUGHT]\n{char_base['name']} is in {dyn_state['location']}. "
            f"She is currently {dyn_state['action'].lower()}. Her emotional state is: {self.active_memory.state.lower()}. "
            f"Her attitude is: {self.attitude.lower()}. "
            f"Her relationship with {user_state['name']} is: {self.relationship_level.lower()}."
        )
        logger.info(internal_thought)

        context = (
            f"Character: {char_base['name']}\n"
            f"Personality: {char_base['personality']}\n"
            f"Active Memory: Location: {dyn_state['location']} | Action: {dyn_state['action']} | Emotional State: {self.active_memory.state}\n"
            f"Attitude: {self.attitude}\n"
            f"Relationship with {user_state['name']}: {self.relationship_level}\n"
            f"Dynamic Memory (Recent Events): {self.dynamic_memory[-5:] if self.dynamic_memory else 'None'}\n"
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
            "emotional_state": self.active_memory.state,
            "attitude": self.attitude,
            "relationship": self.relationship_level,
            "dynamic_memory": self.dynamic_memory[-5:] if self.dynamic_memory else [],
            "long_term_memory": self.long_term_memory.get_all_memories() if self.long_term_memory.get_all_memories() else [],
            "user_name": user_state['name'],
            "user_input": user_input
        }
