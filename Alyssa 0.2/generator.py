# generator.py (Option 2 Implementation + Using Time + New Fallback)
import requests
import logging
import random
import json
import re
from collections import deque

# Logging setup (ensure it's configured)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(filename="debug.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", filemode="a", encoding='utf-8')
logger = logging.getLogger(__name__)

class RPDialogueGenerator:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # TODO: Move API Key to environment variable or secure config
        self.api_key = "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"
        self.used_phrases = set()
        self.phrase_alternatives = {
             "not making a coherent argument": ["Your logic’s all over the place", "That doesn’t add up at all", "You’re not making any sense", "What are you even getting at?"],
             "play the victim card": ["Always acting like the underdog", "Stop painting yourself as the hero", "Quit dodging responsibility", "Don’t pull that pity act"],
             "you’re really making this difficult": ["This is harder than it needs to be", "You’re complicating everything", "Why make this such a hassle?", "You’re turning this into a mess"]
        }
        self.fallback_actions = ["*Looks around.*", "*Pauses thoughtfully.*", "*Sighs softly.*", "*Shifts weight.*", "*Remains silent for a moment.*"]


    def _generate_narrative_action(self, context):
        """Generates the character's narrative action using a dedicated API call."""
        # (Implementation remains the same as previous version in the Canvas)
        # ... (code for generating action) ...
        logger.info("Generating narrative action...")
        emotional_guidance = context.get("emotional_guidance", {})
        char_name = context.get('character_name', 'Character')
        location = context.get('location', 'Unknown')
        current_task = context.get('action', 'doing something').lower() # General task
        previous_action = context.get('previous_action', 'None') # Action from last turn
        user_name = context.get('user_name', 'User')
        user_input = context.get('user_input', '')
        current_time_str = context.get('current_time_in_roleplay', 'Unknown time')

        emo_state = emotional_guidance.get('emotional_state', ['neutral'])
        attitude = emotional_guidance.get('attitude', 'neutral').lower()
        tone = emotional_guidance.get('tone', 'neutral').lower()

        action_prompt = (
            f"You are writing the actions for a character named {char_name}. "
            f"Previous action: {previous_action}. "
            f"Current situation: In {location}, currently {current_task}. The current time is {current_time_str}. "
            f"Their emotional state is {', '.join(emo_state)} with an overall attitude of {attitude} and tone of {tone}. "
            f"{user_name} just said: '{user_input}'.\n\n"
            f"Generate a brief narrative action (1-2 sentences, enclosed in asterisks like *action description*) describing what {char_name} physically does *next* in response to the situation, the user's input, and the current time. "
            f"The action should be consistent with the character's emotional state, attitude, location, time, and the previous action. Show progression or reaction. "
            f"Examples: *Sighs and turns back to the project notes.* / *Stands up abruptly, checking the clock.* / *Walks slowly alongside {user_name} as evening approaches.* / *Forces a smile, but her eyes remain cold.*"
            f"Output only the action description in asterisks."
        )

        headers = { "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json" }
        payload = {
            "model": "meta-llama/llama-4-maverick:free",
            "messages": [{"role": "user", "content": action_prompt}],
            "max_tokens": 75,
            "temperature": 0.7,
        }

        narrative_action = random.choice(self.fallback_actions)
        try:
            logger.info(f"Sending ACTION generation payload (model: {payload.get('model')})")
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            response_json = response.json()
            logger.debug(f"ACTION API Raw Response: {response_json}")
            if "choices" in response_json and response_json["choices"]:
                generated_text = response_json["choices"][0].get("message", {}).get("content", "").strip()
                if generated_text.startswith("*") and generated_text.endswith("*"):
                    narrative_action = generated_text
                    logger.info(f"Generated narrative action via API: '{narrative_action}'")
                elif generated_text:
                     logger.warning(f"Generated action text missing asterisks: '{generated_text}'. Wrapping.")
                     narrative_action = f"*{generated_text.strip()}*"
                else:
                     logger.warning("Action API returned empty content.")
            else:
                logger.warning(f"Unexpected Action API response format: {response_json}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Action API Request Error: {e}", exc_info=True)
        except Exception as e:
             logger.error(f"Unexpected error during Action API call: {e}", exc_info=True)

        logger.info(f"Selected narrative action: {narrative_action}")
        return narrative_action


    def generate_response(self, context, image_url=None):
        """Generates the AI's response including dialogue and actions."""
        logger.info("--- Starting Response Generation ---")
        emotional_guidance = context.get("emotional_guidance", {})

        # --- STEP 1: Generate Narrative Action ---
        narrative_action = self._generate_narrative_action(context)

        # --- STEP 2: Build Prompt for Dialogue ---
        dialogue_prompt = self._build_dialogue_prompt(context, emotional_guidance, narrative_action)

        # --- STEP 3: Call API for Dialogue ---
        messages = [{"role": "system", "content": f"You are {context.get('character_name', 'Character')}. Generate only the dialogue that follows the provided action."}]
        if image_url:
             logger.warning("Image URL provided, adding info to dialogue prompt.")
             messages.append({
                 "role": "user",
                 "content": [{"type": "text", "text": dialogue_prompt + f"\n(User also provided an image: {image_url})"},
                             {"type": "image_url", "image_url": {"url": image_url}}]
             })
        else:
             messages.append({"role": "user", "content": dialogue_prompt})

        headers = { "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json" }
        payload = {
            "model": "meta-llama/llama-4-maverick:free",
            "messages": messages,
            "max_tokens": 400,
            "temperature": 0.75
        }

        # --- START CHANGE: Updated Default Fallback Dialogue ---
        dialogue_text = "*Poppy shrugs.* 'Uh, somethin's busted. Deal with it.'" # New default fallback
        # --- END CHANGE ---
        try:
            logger.info(f"Sending DIALOGUE generation payload (model: {payload.get('model')})")
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            response_json = response.json()
            logger.debug(f"DIALOGUE API Raw Response: {response_json}")
            if "choices" in response_json and response_json["choices"]:
                generated_dialogue = response_json["choices"][0].get("message", {}).get("content", "").strip()
                generated_dialogue = generated_dialogue.replace('"', '').strip() # Basic cleaning
                if generated_dialogue:
                     # Successfully got dialogue, overwrite the fallback
                     dialogue_text = generated_dialogue
                     logger.info(f"Generated dialogue via API: '{dialogue_text[:100]}...'")
                else:
                     logger.warning("Dialogue API returned empty content. Using fallback.")
                     # Keep the default fallback assigned above
            else:
                logger.warning(f"Unexpected Dialogue API response format: {response_json}. Using fallback.")
                # Keep the default fallback assigned above

        except requests.exceptions.RequestException as e:
            logger.error(f"Dialogue API Request Error: {e}", exc_info=True)
            # Keep the default fallback assigned above, maybe add error detail?
            # dialogue_text += f" (Error: {e})" # Optional: Append error info
        except Exception as e:
             logger.error(f"Unexpected error during Dialogue API call: {e}", exc_info=True)
             # Keep the default fallback assigned above
             # dialogue_text += f" (Error: {e})" # Optional: Append error info


        # --- STEP 4: Combine Action and Dialogue ---
        final_ai_response = f"{narrative_action}\n\n{dialogue_text}"

        # --- Post-processing ---
        for phrase in self.phrase_alternatives:
            if phrase in final_ai_response:
                self.used_phrases.add(phrase)

        logger.info("--- Finished Response Generation ---")
        return final_ai_response, final_ai_response


    def _build_dialogue_prompt(self, context, emotional_guidance, narrative_action):
         """Constructs the prompt for the LLM to generate ONLY dialogue."""
         # (Implementation remains the same as previous version in the Canvas)
         # ... (code for building dialogue prompt, including time) ...
         char_name = context.get('character_name', 'Character')
         personality = context.get('personality', 'Unknown')
         location = context.get('location', 'Unknown')
         current_task = context.get('action', 'doing something').lower()
         user_name = context.get('user_name', 'User')
         user_input = context.get('user_input', '')
         previous_action = context.get('previous_action', 'None')
         current_time_str = context.get('current_time_in_roleplay', 'Unknown time') # Get time

         emo_state = emotional_guidance.get('emotional_state', ['neutral'])
         internal_feeling = emotional_guidance.get('internal_feeling', 'neutral')
         expressed_feeling = emotional_guidance.get('expressed_feeling', 'neutral')
         attitude = emotional_guidance.get('attitude', 'neutral').lower()
         tone = emotional_guidance.get('tone', 'neutral').lower()
         active_defenses = emotional_guidance.get('active_defenses', [])
         relationship = emotional_guidance.get('relationship', 'neutral').lower()

         dynamic_memory_str = ", ".join(context.get('dynamic_memory', [])) if context.get('dynamic_memory') else 'None'
         active_memory_list = context.get('active_memory', [])
         active_memory_str = ", ".join(active_memory_list) if active_memory_list else 'None'
         ltm_list = context.get('long_term_memory', [])
         long_term_memory_str = "\n".join(ltm_list) if ltm_list else 'None'

         prompt = (
             f"You are roleplaying as {char_name} ({personality}).\n"
             f"Current situation: In {location}, {current_task}. The current time is approximately {current_time_str}.\n"
             f"Character's emotional state: {', '.join(emo_state)} (Internal: {internal_feeling}, Expressed: {expressed_feeling}, Attitude: {attitude}).\n"
             f"Active defenses: {', '.join(active_defenses) if active_defenses else 'None'}.\n"
             f"Relationship with {user_name}: {relationship}.\n"
             f"Relevant Memory Context:\n"
             f"  Dynamic: {dynamic_memory_str}\n"
             f"  Active: {active_memory_str}\n"
             f"  LTM:\n{long_term_memory_str}\n"
             f"Previous narrative action taken by {char_name}: {previous_action}\n"
             f"{user_name} just said: '{user_input}'\n\n"
             f"Action {char_name} just performed: {narrative_action}\n\n"
             f"TASK: Generate ONLY the dialogue spoken by {char_name} immediately following this action. "
             f"The dialogue should be consistent with all the context provided (personality, emotion, attitude, tone: {tone}, defenses, relationship, memories, time, user input, and the action just performed). "
             f"Do NOT include action descriptions or asterisks. Output only the spoken words."
             f"Avoid reusing these specific phrases if possible: {', '.join(self.used_phrases) if self.used_phrases else 'None'}."
         )
         logger.debug(f"Generated DIALOGUE prompt (first 200 chars): {prompt[:200]}...")
         return prompt

    # Fallback function - might not be needed if default dialogue_text is used
    # def _generate_fallback_response(self, context, narrative_action, error_reason="API Error"):
    #      # ... (implementation) ...
    #      pass

