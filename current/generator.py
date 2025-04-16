import requests
import logging
import random
import json
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
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = "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"
        logger.info(f"DEBUG: API Key = '{self.api_key}'")
        # Track used phrases to avoid repetition
        self.used_phrases = set()
        # Track recent nonverbal actions with a message counter (soft lock)
        self.recent_nonverbals = deque(maxlen=3)  # Stores (action, message_count) tuples
        self.message_count = 0  # Tracks total messages to manage cooldown
        # Pre-made phrase alternatives for dialogue variety
        self.phrase_alternatives = {
            "not making a coherent argument": [
                "Your logic’s all over the place",
                "That doesn’t add up at all",
                "You’re not making any sense",
                "What are you even getting at?"
            ],
            "play the victim card": [
                "Always acting like the underdog",
                "Stop painting yourself as the hero",
                "Quit dodging responsibility",
                "Don’t pull that pity act"
            ],
            "you’re really making this difficult": [
                "This is harder than it needs to be",
                "You’re complicating everything",
                "Why make this such a hassle?",
                "You’re turning this into a mess"
            ]
        }

    def generate_response(self, context, image_url=None):
        emotional_guidance = context["emotional_guidance"]
        self.message_count += 1  # Increment message counter for each response

        # Extract recent events to identify used phrases
        recent_events = context['dynamic_memory'] if context['dynamic_memory'] else []
        for event in recent_events:
            if f"{context['character_name']} responded" in event:
                response = event.split(f"{context['character_name']} responded:")[1]
                for phrase in self.phrase_alternatives:
                    if phrase in response:
                        self.used_phrases.add(phrase)

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
            f"You are {context['character_name']}, a character with the personality: {context['personality']}. "
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
            f"Instead, use fresh expressions like: {', '.join([random.choice(self.phrase_alternatives.get(p, [p])) for p in self.used_phrases]) if self.used_phrases else 'None'}. "
            f"If you need to express frustration, disagreement, or other sentiments, create fresh dialogue that fits the character's personality and mood. "
            f"For example, instead of 'You’re making this difficult,' try something like 'Why do you keep throwing wrenches in this?'"
        )

        # Prepare API payload
        messages = [
            {"role": "system", "content": f"You are {context['character_name']}, follow the prompt instructions."}
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "RoleplayBot"
        }

        payload = {
            "model": "meta-llama/llama-4-maverick:free",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }

        try:
            logger.info(f"DEBUG: Sending payload = {json.dumps(payload, indent=2)}")
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                ai_text = response_json["choices"][0]["message"]["content"].strip()
                logger.info(f"DEBUG: Response = {response_json}")
            else:
                logger.info(f"Unexpected response: {response_json}")
                ai_text = self._generate_fallback_response(context, nonverbal_cues)
        except requests.exceptions.RequestException as e:
            logger.info(f"API Error: {str(e)} - Status: {response.status_code if 'response' in locals() else 'No response'}")
            logger.info(f"DEBUG: Response text = {response.text if 'response' in locals() else 'N/A'}")
            ai_text = self._generate_fallback_response(context, nonverbal_cues)
            # *Poppy shrugs.* 'Uh, somethin’s busted. Deal with it. (That words are my real nightmare fr)

        dialogue = ai_text
        if '*' in ai_text and "'" in ai_text:
            try:
                dialogue = ai_text.split("'", 1)[1].rsplit("'", 1)[0].strip()
            except IndexError:
                pass

        # Update used phrases with the new response
        for phrase in self.phrase_alternatives:
            if phrase in ai_text:
                self.used_phrases.add(phrase)

        # Update recent nonverbal actions
        self._update_nonverbal_history(nonverbal_cues)

        return ai_text, dialogue

    def _filter_nonverbal_cues(self, nonverbal_cues, emotional_guidance):
        """Filter out nonverbal cues that are on cooldown unless the situation permits reuse."""
        filtered_cues = []
        # Expanded pre-made nonverbal actions, grouped by emotional tone
        alternative_cues = {
            "Shrugs her arms": ["Taps her foot", "Tilts her head", "Crosses her arms", "Rolls her eyes", "Fidgets with her hair"],
            "Collapses to knees": ["Sinks into a chair", "Covers her face", "Stumbles back", "Clutches her chest", "Drops her shoulders"],
            "Hands trembling": ["Clenches her fists", "Grips her sleeves", "Bites her lip", "Twists her ring", "Wipes her palms"],
            "Face contorted with grief": ["Eyes widen in shock", "Mouth trembles", "Looks away quickly", "Buries face in hands", "Swallows hard"],
            "Takes a shaky step forward": ["Leans forward slightly", "Steps closer hesitantly", "Reaches out briefly", "Pauses mid-step", "Shuffles nervously"],
            "Voice breaking": ["Voice cracks", "Words falter", "Speaks in a whisper", "Chokes on words", "Trails off quietly"],
            "Shaky step forward": ["Hesitates mid-step", "Shuffles closer", "Pauses abruptly", "Sways slightly", "Glances down nervously"],
            "Tears streaming down face": ["Eyes glisten with tears", "Wipes at her eyes", "Blinks rapidly", "Sniffles softly", "Tears pool in eyes"],
            "Voice barely above a whisper": ["Speaks softly", "Murmurs under her breath", "Whispers hoarsely", "Mumbles faintly", "Sighs quietly"],
            # New neutral actions
            "Leans forward slightly": ["Nods eagerly", "Points for emphasis", "Gestures animatedly", "Rests chin on hand", "Taps pencil on desk"],
            "Arms crossed": ["Taps fingers on arm", "Shifts weight to one foot", "Glances sideways", "Huffs softly", "Raises an eyebrow"],
            # New emotional actions
            "Softer voice": ["Lowers her gaze", "Smiles faintly", "Tilts her head gently", "Brushes hair back", "Relaxes her shoulders"],
            "Maintains more eye contact": ["Nods slowly", "Leans in closer", "Holds gaze steadily", "Blinks softly", "Smirks lightly"]
        }

        # Emotional state requirements for reusing cues
        emotional_state_requirements = {
            "Shrugs her arms": ["Neutral", "Isolated", "In Control"],
            "Collapses to knees": ["Grieving", "Powerless"],
            "Hands trembling": ["Grieving", "Desperate", "Vulnerable"],
            "Face contorted with grief": ["Grieving"],
            "Takes a shaky step forward": ["Desperate", "Vulnerable"],
            "Voice breaking": ["Grieving", "Desperate"],
            "Shaky step forward": ["Vulnerable"],
            "Tears streaming down face": ["Grieving", "Vulnerable"],
            "Voice barely above a whisper": ["Vulnerable"],
            "Leans forward slightly": ["Neutral", "Connected", "Affirmed"],
            "Arms crossed": ["Neutral", "Isolated", "Invalidated"],
            "Softer voice": ["Connected", "Authentic", "Opening Up"],
            "Maintains more eye contact": ["Connected", "Authentic", "In Control"]
        }

        current_emotional_state = emotional_guidance['emotional_state']

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
                # Try pre-made alternatives first
                alternatives = alternative_cues.get(cue, [])
                available_alternatives = [alt for alt in alternatives 
                                        if not any(alt.lower() == rc.lower() for rc, _ in self.recent_nonverbals)]
                if available_alternatives:
                    filtered_cues.append(random.choice(available_alternatives))
                else:
                    # Generate a new action via API
                    new_cue = self._generate_nonverbal_cue(emotional_guidance)
                    filtered_cues.append(new_cue)
            else:
                filtered_cues.append(cue)

        return filtered_cues

    def _generate_nonverbal_cue(self, emotional_guidance):
        """Generate a new nonverbal action via API based on emotional state."""
        prompt = (
            f"Generate a unique nonverbal action for a character in the emotional state: {', '.join(emotional_guidance['emotional_state'])}. "
            f"The action should be subtle, natural, and fit their current mood (attitude: {emotional_guidance['attitude'].lower()}). "
            f"Examples: 'Taps her foot', 'Clenches her fists', 'Smiles faintly'. "
            f"Avoid actions already used recently: {', '.join([cue for cue, _ in self.recent_nonverbals]) if self.recent_nonverbals else 'None'}. "
            f"Return one action as plain text."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "RoleplayBot"
        }

        payload = {
            "model": "meta-llama/llama-4-maverick:free",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50,
            "temperature": 0.9
        }

        try:
            logger.info(f"DEBUG: Sending nonverbal payload = {json.dumps(payload, indent=2)}")
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                new_cue = response_json["choices"][0]["message"]["content"].strip()
                logger.info(f"Generated nonverbal cue: {new_cue}")
                return new_cue
            else:
                logger.info(f"Unexpected nonverbal response: {response_json}")
                return random.choice(["Adjusts her posture", "Looks away briefly"])
        except requests.exceptions.RequestException as e:
            logger.info(f"Nonverbal API Error: {str(e)}")
            return random.choice(["Adjusts her posture", "Looks away briefly"])  # Fallback

    def _update_nonverbal_history(self, nonverbal_cues):
        """Update the history of nonverbal actions with the current message count."""
        for cue in nonverbal_cues:
            self.recent_nonverbals.append((cue, self.message_count))

    def _generate_fallback_response(self, context, nonverbal_cues):
        """Generate a fallback response locally when the API fails."""
        emotional_guidance = context["emotional_guidance"]
        user_name = context["user_name"]
        attitude = emotional_guidance["attitude"].lower()
        tone = emotional_guidance["tone"].lower()

        # Construct nonverbal description
        nonverbal_description = f"*{context['character_name']} {nonverbal_cues[0].lower()}"
        if len(nonverbal_cues) > 1:
            nonverbal_description += f", {nonverbal_cues[1].lower()}"
        if len(nonverbal_cues) > 2:
            nonverbal_description += f", {nonverbal_cues[2].lower()}"
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