# generator_local_only.py (Local Ollama Only Version)
import requests
import logging
import random
import json
import re
from collections import deque

# Logging setup
if not logging.getLogger().hasHandlers():
    logging.basicConfig(filename="debug.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", filemode="a", encoding='utf-8')
# Get logger for this module
logger = logging.getLogger('generator') # Use named logger


# --- Renamed Local Generator (was LocalGenerator) ---
class RPDialogueGenerator: # Renamed from LocalGenerator
    def __init__(self, model_name, ollama_base_url="http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = f"{ollama_base_url.rstrip('/')}/api/chat" # Use chat endpoint
        self.used_phrases = set()
        self.phrase_alternatives = {
             "not making a coherent argument": ["Your logic’s all over the place", "That doesn’t add up at all", "You’re not making any sense", "What are you even getting at?"],
             "play the victim card": ["Always acting like the underdog", "Stop painting yourself as the hero", "Quit dodging responsibility", "Don’t pull that pity act"],
             "you’re really making this difficult": ["This is harder than it needs to be", "You’re complicating everything", "Why make this such a hassle?", "You’re turning this into a mess"]
        }
        self.fallback_actions = ["*Looks around.*", "*Pauses thoughtfully.*", "*Sighs softly.*", "*Shifts weight.*", "*Remains silent for a moment.*"]
        self.fallback_dialogue = "*Poppy shrugs.* 'Uh, somethin's busted. Deal with it.'"
        logger.debug(f"RPDialogueGenerator (Local Ollama Mode) initialized for model '{model_name}' at {ollama_base_url}")

    def _call_ollama_api(self, prompt, max_tokens, temperature):
        """Helper function to call the Ollama chat API."""
        # Use a system prompt if beneficial for the model (Llama 3 often benefits)
        messages = [
            # {"role": "system", "content": "You are a helpful assistant generating text for a roleplay character."}, # Optional system prompt
            {"role": "user", "content": prompt}
        ]
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens # Ollama uses num_predict for max_tokens
                # Add other Ollama options here (e.g., top_p, top_k)
            }
        }
        headers = {"Content-Type": "application/json"}
        response_text = ""
        try:
            logger.info(f"Sending payload to Ollama API (model: {self.model_name})")
            # logger.debug(f"Ollama Payload: {json.dumps(payload, indent=2)}") # Careful logging full prompts
            response = requests.post(self.ollama_url, headers=headers, json=payload, timeout=60) # Add timeout
            response.raise_for_status()
            response_json = response.json()
            logger.debug(f"Ollama Raw Response: {response_json}")

            # Extract content based on Ollama's typical chat response structure
            if "message" in response_json and "content" in response_json["message"]:
                 response_text = response_json["message"]["content"].strip()
                 if not response_text:
                      logger.warning("Ollama API returned empty content.")
                 else:
                      logger.info(f"Response received successfully from Ollama: '{response_text[:100]}...'")
            # Handle potential older Ollama format or errors within response
            elif "response" in response_json: # Sometimes Ollama puts response here
                 response_text = response_json["response"].strip()
                 if not response_text:
                      logger.warning("Ollama API returned empty 'response' field.")
                 else:
                      logger.info(f"Response received successfully from Ollama (using 'response' field): '{response_text[:100]}...'")
            elif "error" in response_json:
                 logger.error(f"Ollama API returned an error in response: {response_json['error']}")
                 # Keep response_text empty to trigger fallback later
            else:
                logger.warning(f"Unexpected Ollama response format: {response_json}")

        except requests.exceptions.Timeout:
             logger.error("Ollama API request timed out.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API Request Error: {e}", exc_info=True)
            status_code = e.response.status_code if e.response is not None else "N/A"
            response_body = e.response.text if e.response is not None else "N/A"
            logger.error(f"Ollama Error Details - Status: {status_code}, Response Text: {response_body[:500]}...")
        except Exception as e:
             logger.error(f"Unexpected error during Ollama API call: {e}", exc_info=True)

        return response_text


    def _generate_narrative_action(self, context):
        """Generates narrative action via Local Ollama API."""
        logger.info("Generating narrative action via Local Ollama...")
        # (Build action_prompt - same as before)
        emotional_guidance = context.get("emotional_guidance", {})
        char_name = context.get('character_name', 'Character')
        location = context.get('location', 'Unknown')
        current_task = context.get('action', 'doing something').lower()
        previous_action = context.get('previous_action', 'None')
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

        # Call Ollama API for action
        generated_text = self._call_ollama_api(action_prompt, max_tokens=75, temperature=0.7)

        narrative_action = random.choice(self.fallback_actions) # Default fallback
        if generated_text:
             # Basic validation/cleaning
             if generated_text.startswith("*") and generated_text.endswith("*"):
                 narrative_action = generated_text
             else:
                 # Attempt to wrap if missing asterisks but looks like an action
                 logger.warning(f"Generated action text missing asterisks (Local): '{generated_text}'. Wrapping.")
                 narrative_action = f"*{generated_text.strip()}*"
        else:
             logger.warning("Local action generation failed or returned empty, using fallback action.")


        logger.info(f"Selected narrative action (Local): {narrative_action}")
        return narrative_action

    def _build_dialogue_prompt(self, context, emotional_guidance, narrative_action):
         """Constructs the prompt for the LLM to generate ONLY dialogue."""
         # (Implementation remains the same)
         char_name = context.get('character_name', 'Character')
         personality = context.get('personality', 'Unknown')
         location = context.get('location', 'Unknown')
         current_task = context.get('action', 'doing something').lower()
         user_name = context.get('user_name', 'User')
         user_input = context.get('user_input', '')
         previous_action = context.get('previous_action', 'None')
         current_time_str = context.get('current_time_in_roleplay', 'Unknown time')

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


    def generate_response(self, context, image_url=None):
        """Generates the AI's response using the Local Ollama API."""
        logger.info("--- Starting Local Response Generation ---")
        emotional_guidance = context.get("emotional_guidance", {})

        # STEP 1: Generate Narrative Action via Local API
        narrative_action = self._generate_narrative_action(context) # This now uses _call_ollama_api

        # STEP 2: Build Prompt for Dialogue
        dialogue_prompt = self._build_dialogue_prompt(context, emotional_guidance, narrative_action)

        # STEP 3: Call Local API for Dialogue
        if image_url:
            logger.warning("Image URL provided, but Local Ollama generator cannot process it directly in this implementation. Ignoring image.")
            # Optionally add text description to prompt if available from context
            # dialogue_prompt += f"\n(User also provided an image: {context.get('user_input', '')})"


        dialogue_text = self.fallback_dialogue # Default fallback
        generated_dialogue = self._call_ollama_api(dialogue_prompt, max_tokens=400, temperature=0.75)

        if generated_dialogue:
            # Basic cleaning - remove quotes often added by models
            dialogue_text = generated_dialogue.replace('"', '').strip()
            logger.info(f"Generated dialogue via Local Ollama: '{dialogue_text[:100]}...'")
        else:
            logger.warning("Local dialogue generation failed or returned empty. Using fallback dialogue.")


        # STEP 4: Combine Action and Dialogue
        final_ai_response = f"{narrative_action}\n\n{dialogue_text}"

        # Post-processing
        for phrase in self.phrase_alternatives:
            if phrase in final_ai_response:
                self.used_phrases.add(phrase)

        logger.info("--- Finished Local Response Generation ---")
        # Return the combined text for both display and memory
        return final_ai_response, final_ai_response

