import openai
import logging

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

    def generate_response(self, context, image_url=None):
        emotional_guidance = context["emotional_guidance"]
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
            f"Nonverbal cues to include: {', '.join(emotional_guidance['nonverbal_cues']) if emotional_guidance['nonverbal_cues'] else 'None'}. "
            f"Active defense mechanisms: {', '.join(emotional_guidance['active_defenses']) if emotional_guidance['active_defenses'] else 'None'}. "
            f"Your relationship with {context['user_name']} is {emotional_guidance['relationship'].lower()}. "
            f"Recent events: {context['dynamic_memory'] if context['dynamic_memory'] else 'None'}. "
            f"Long-term memories: {context['long_term_memory'] if context['long_term_memory'] else 'None'}. "
            f"{context['user_name']} just said: '{context['user_input']}'. "
            f"Respond as {context['character_name']}, keeping your tone, attitude, and personality consistent with your emotional state. "
            f"Include a short action description in asterisks before your dialogue, incorporating the specified nonverbal cues to reflect your current mood. "
            f"Ensure your response builds on previous interactions, showing gradual emotional transitions if your mood changes. "
            f"Reflect your emotional conflicts and defense mechanisms in your dialogue and actions. "
            f"Avoid abrupt mood swings—make any change feel natural and motivated by the context."
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
            ai_text = f"*Poppy shrugs, her expression unreadable.* 'Something’s broken, {context['user_name']}. Figure it out.'"
            logger.info(f"API Error: {str(e)}")

        dialogue = ai_text
        if '*' in ai_text and "'" in ai_text:
            try:
                dialogue = ai_text.split("'", 1)[1].rsplit("'", 1)[0].strip()
            except IndexError:
                pass

        return ai_text, dialogue
