import openai
import logging
import random
import json
import requests
from collections import deque

# Set up logging
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filemode="a"
)
logger = logging.getLogger()

class RPDialogueGenerator:
    def __init__(self):
        openai.api_base = "https://openrouter.ai/api/v1"
        openai.api_key = "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"
        logger.info(f"DEBUG: API Key = '{openai.api_key}'")
        # Track used phrases to avoid repetition
        self.used_phrases = set()
        # Track recent nonverbal actions with a message counter (soft lock)
        self.recent_nonverbals = deque(maxlen=3)  # Stores (action, message_count) tuples
        self.message_count = 0  # Tracks total messages to manage cooldown

    def generate_response(self, context, image_url=None):
        emotional_guidance = context["emotional_guidance"]
        self.message_count += 1  # Increment message counter for each response

        # Extract recent events to identify used phrases
        recent_events = context['dynamic_memory'] if context['dynamic_memory'] else []
        for event in recent_events:
            if "Poppy responded" in event:
                response = event.split("Poppy responded:")[1]
                if "not making a coherent argument" in response:
                    self.used_phrases.add("not making a coherent argument")
                if "play the victim card" in response:
                    self.used_phrases.add("play the victim card")
                if "you’re really making this difficult" in response:
                    self.used_phrases.add("you’re really making this difficult")

        # Override nonverbal cues for high-impact emotional states
        nonverbal_cues = emotional_guidance['nonverbal_cues']
        if emotional_guidance['attitude'].lower() == "grieving":
            nonverbal_cues = ["Collapses to knees", "Hands trembling", "Face contorted with grief"]
        elif emotional_guidance['attitude'].lower() == "desperate":
            nonverbal_cues = ["Takes a shaky step forward", "Hands trembling", "Voice breaking"]
        elif emotional_guidance['attitude'].lower() == "vulnerable":
            nonverbal_cues = ["Shaky step forward", "Tears streaming down face", "Voice barely above a whisper"]

        # Check if any nonverbal cues are on cooldown and replace them if needed
        nonverbal_cues = self._filter_nonverbal_cues(nonverbal_cues, emotional_guidance)

        # Construct the prompt with additional instructions for variety
        prompt = (
            f"You are {context['character_name']}, a 21-year-old college student known as the queen of the school. "
            f"Your personality is {context['personality']}. "
            f"You’re currently in {context['location']}, {context['action'].lower()}. "
            f"Your current emotional state is {', '.join(emotional_guidance['emotional_state']).lower()}. "
            f"You feel {emotional_guidance['internal_feeling']} internally, but you’re expressing {emotional_guidance['expressed_feeling']}. "
            f"Your facade intensity is {emotional_guidance['facade_intensity']:.2f} (0-1 scale, higher means a larger gap between internal and expressed emotions). "
            f"Your attitude is {emotional_guidance['attitude'].lower()}—reflect this in your tone and behavior. "
            f"You have the following emotional conflicts: {', '.join(emotional_guidance['emotional_conflicts']) if emotional_guidance['emotional_conflicts'] else 'None'}. "
            f"Your tone should be {emotional_guidance['tone'].lower()}. "
            f"Nonverbal cues to include: {', '.join(nonverbal_cues) if nonverbal_cues else 'None'}. "
            f"Active defense mechanisms: {', '.join(emotional_guidance['active_defenses']) if emotional_guidance['active_defenses'] else 'None'}. "
            f"Your relationship with {context['user_name']} is {emotional_guidance['relationship'].lower()}. "
            f"Recent events: {context['dynamic_memory'] if context['dynamic_memory'] else 'None'}. "
            f"Long-term memories: {context['long_term_memory'] if context['long_term_memory'] else 'None'}. "
            f"{context['user_name']} just said: '{context['user_input']}'. "
            f"Respond as {context['character_name']}, keeping your tone, attitude, and personality consistent with your emotional state. "
            f"Include a short action description in asterisks before your dialogue, incorporating the specified nonverbal cues to reflect your current mood. "
            f"Ensure your response builds on previous interactions, showing gradual emotional transitions if your mood changes. "
            f"Reflect your emotional conflicts and defense mechanisms in your dialogue and actions. "
            f"Avoid abrupt mood swings—make any change feel natural and motivated by the context. "
            f"To ensure variety, avoid reusing the following phrases: {', '.join(self.used_phrases) if self.used_phrases else 'None'}. "
            f"Instead, use fresh expressions that convey similar sentiments if needed."
        )

        messages = [
            {"role": "system", "content": "You are Poppy, follow the prompt instructions."}
        ]

        if image_url:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt})

        headers = {
            "HTTP-Referer": "http://localhost",
            "X-Title": "PoppyBot"
        }

        try:
            # *Poppy shrugs.* 'Uh, somethin’s busted. Deal with it. (That words are my real nightmare fr)
            """
            try:
                logger.info(f"DEBUG: Sending payload = {json.dumps(payload, indent=2)}")
                response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
                response.raise_for_status()
                response_json = response.json()
                if "error" in response_json:
                    ai_text = f"*Poppy shrugs.* 'Uh, somethin’s busted, {user_state['name']}. Deal with it.'"
                    logger.info(f"API Error: {response_json['error']}")
                elif "choices" in response_json:
                    ai_text = response_json["choices"][0]["message"]["content"].strip()
                    logger.info(f"DEBUG: Response = {response_json}")
                else:
                    ai_text = f"*Poppy shrugs.* 'Uh, somethin’s busted, {user_state['name']}. Deal with it.'"
                    logger.info(f"Unexpected response: {response_json}")
            except requests.exceptions.RequestException as e:
                ai_text = f"*Poppy shrugs.* 'Uh, somethin’s busted, {user_state['name']}. Deal with it.'"
                logger.info(f"API Error: {e} - Status: {response.status_code if 'response' in locals() else 'No response'}")
                logger.info(f"DEBUG: Response text = {response.text if 'response' in locals() else 'N/A'}")
            """

            logger.info(f"DEBUG: Headers = {headers}")
            logger.info(f"DEBUG: Sending messages = {messages}")
            response = openai.ChatCompletion.create(
                model="meta-llama/llama-4-maverick:free",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                headers=headers
            )
            ai_text = response.choices[0].message['content'].strip()
            logger.info(f"DEBUG: Response = {response}")
        except Exception as e:
            # Improved fallback: Generate a response locally based on emotional guidance
            ai_text = self._generate_fallback_response(context, nonverbal_cues)
            logger.info(f"API Error: {str(e)}")

        dialogue = ai_text
        if '*' in ai_text and "'" in ai_text:
            try:
                dialogue = ai_text.split("'", 1)[1].rsplit("'", 1)[0].strip()
            except IndexError:
                pass

        # Update used phrases with the new response
        if "not making a coherent argument" in ai_text:
            self.used_phrases.add("not making a coherent argument")
        if "play the victim card" in ai_text:
            self.used_phrases.add("play the victim card")
        if "you’re really making this difficult" in ai_text:
            self.used_phrases.add("you’re really making this difficult")

        # Update recent nonverbal actions
        self._update_nonverbal_history(nonverbal_cues)

        return ai_text, dialogue

    def _filter_nonverbal_cues(self, nonverbal_cues, emotional_guidance):
        """Filter out nonverbal cues that are on cooldown unless the situation permits reuse."""
        filtered_cues = []
        alternative_cues = {
            "Shrugs her arms": ["Taps her foot", "Tilts her head", "Crosses her arms"],
            "Collapses to knees": ["Sinks into a chair", "Covers her face", "Stumbles back"],
            "Hands trembling": ["Clenches her fists", "Grips her sleeves", "Bites her lip"],
            "Face contorted with grief": ["Eyes widen in shock", "Mouth trembles", "Looks away quickly"],
            "Takes a shaky step forward": ["Leans forward slightly", "Steps closer hesitantly", "Reaches out briefly"],
            "Voice breaking": ["Voice cracks", "Words falter", "Speaks in a whisper"],
            "Shaky step forward": ["Hesitates mid-step", "Shuffles closer", "Pauses abruptly"],
            "Tears streaming down face": ["Eyes glisten with tears", "Wipes at her eyes", "Blinks rapidly"],
            "Voice barely above a whisper": ["Speaks softly", "Murmurs under her breath", "Whispers hoarsely"]
        }

        # Check if the situation permits reusing a cue (e.g., matching emotional state)
        current_emotional_state = emotional_guidance['emotional_state']
        emotional_state_requirements = {
            "Shrugs her arms": ["Neutral", "Isolated", "In Control"],
            "Collapses to knees": ["Grieving", "Powerless"],
            "Hands trembling": ["Grieving", "Desperate", "Vulnerable"],
            "Face contorted with grief": ["Grieving"],
            "Takes a shaky step forward": ["Desperate", "Vulnerable"],
            "Voice breaking": ["Grieving", "Desperate"],
            "Shaky step forward": ["Vulnerable"],
            "Tears streaming down face": ["Grieving", "Vulnerable"],
            "Voice barely above a whisper": ["Vulnerable"]
        }

        for cue in nonverbal_cues:
            # Check if the cue is on cooldown
            on_cooldown = False
            for recent_cue, msg_count in self.recent_nonverbals:
                if cue.lower() == recent_cue.lower() and (self.message_count - msg_count) <= 3:
                    # Check if the situation permits reuse
                    required_states = emotional_state_requirements.get(cue, [])
                    if any(state in current_emotional_state for state in required_states):
                        filtered_cues.append(cue)  # Situation permits reuse
                    else:
                        on_cooldown = True
                    break

            if on_cooldown:
                # Replace with an alternative cue
                alternatives = alternative_cues.get(cue, ["Adjusts her posture"])
                available_alternatives = [alt for alt in alternatives if not any(alt.lower() == rc.lower() for rc, _ in self.recent_nonverbals)]
                replacement = random.choice(available_alternatives if available_alternatives else alternatives)
                filtered_cues.append(replacement)
            else:
                filtered_cues.append(cue)

        return filtered_cues

    def _update_nonverbal_history(self, nonverbal_cues):
        """Update the history of nonverbal actions with the current message count."""
        for cue in nonverbal_cues:
            self.recent_nonverbals.append((cue, self.message_count))

    def _generate_fallback_response(self, context, nonverbal_cues):
        """Generate a fallback response locally when the API fails"""
        emotional_guidance = context["emotional_guidance"]
        user_name = context["user_name"]
        attitude = emotional_guidance["attitude"].lower()
        tone = emotional_guidance["tone"].lower()

        # Construct nonverbal description
        nonverbal_description = f"*I {nonverbal_cues[0].lower()}"
        if len(nonverbal_cues) > 1:
            nonverbal_description += f", my {nonverbal_cues[1].lower()}"
        if len(nonverbal_cues) > 2:
            nonverbal_description += f", my {nonverbal_cues[2].lower()}"
        nonverbal_description += ".*"

        # Generate dialogue based on attitude and tone
        if attitude == "grieving":
            dialogue = (
                f"No, this can’t be happening… *I choke on a sob, my voice breaking.* "
                f"{user_name}, please… I didn’t mean for this to happen… I can’t lose you like this!"
            )
        elif attitude == "desperate":
            dialogue = (
                f"Please, {user_name}, don’t do this… *I plead, my voice trembling.* "
                f"I need you—I can’t handle this on my own!"
            )
        elif attitude == "vulnerable":
            dialogue = (
                f"I… I’m so sorry, {user_name}. *My voice trembles, barely above a whisper.* "
                f"I never meant to hurt you… I was just scared."
            )
        elif attitude == "dismissive" and tone == "condescending":
            dialogue = (
                f"Seriously, {user_name}? *I scoff, rolling my eyes.* "
                f"You’re making a big deal out of nothing. Get over it."
            )
        else:
            dialogue = (
                f"I don’t know what to say, {user_name}. *I sigh, my tone neutral.* "
                f"Can we just move on?"
            )

        return f"{nonverbal_description}\n\n{dialogue}"