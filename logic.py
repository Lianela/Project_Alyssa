import logging
from active_memory import ActiveMemoryFile
from character_memory import CharacterMemory, UserMemory
from long_term_memory import LongTermMemoryFile

# Set up logging
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filemode="a"
)
logger = logging.getLogger()

class EmotionalCore:
    def __init__(self):
        # Core emotional dimensions
        self.emotions = {
            "vulnerability": 0.2,     # Feeling exposed/protected
            "connection": 0.1,        # Feeling close/distant
            "autonomy": 0.8,          # Feeling in control/controlled
            "validation": 0.3,        # Feeling affirmed/rejected
            "authenticity": 0.4,      # Feeling true/false to self
            "psychological_safety": 0.2  # Environment feels safe/threatening
        }
        
        # Separate internal vs. expressed emotions
        self.internal_emotions = self.emotions.copy()
        self.expressed_emotions = {k: v for k, v in self.emotions.items()}
        
        # Defense mechanism strength
        self.defense_activation = 0.7
        self.active_defenses = []
        
        # Memory with emotional context
        self.emotional_memories = []
        self.emotional_triggers = {}
        
        # Relationship tracking
        self.trust_threshold = 0.5
        self.intimacy_level = 0.1
        self.psychological_distance = 0.9
        
        # Personality baseline (Poppy's starting traits)
        self.personality = {
            "pride": 0.8,
            "fear_of_vulnerability": 0.7, 
            "need_for_control": 0.8,
            "emotional_awareness": 0.4,
            "empathy": 0.3,
            "authenticity": 0.4
        }
        
        # Emotional stability and volatility
        self.emotional_inertia = 0.7
        self.emotional_volatility = 0.4
        
        # Unconscious patterns
        self.unconscious_patterns = {
            "fear_of_abandonment": 0.6,
            "perfectionism": 0.8,
            "self_worth_contingency": 0.7
        }

    def process_interaction(self, message, context):
        emotional_impact = self._analyze_emotional_content(message)
        triggered_memories = self._check_triggers(message)
        if triggered_memories:
            self._amplify_emotions_from_triggers(emotional_impact, triggered_memories)
        self._update_internal_emotions(emotional_impact, context)
        self._evaluate_defenses()
        self._calculate_expressed_emotions()
        self._update_relationship(message, emotional_impact)
        self._form_emotional_memory(message, emotional_impact, context)
        self._evolve_personality(emotional_impact)
        return self._generate_response_guidance()

    def _analyze_emotional_content(self, message):
        impact = {emotion: 0.0 for emotion in self.emotions}
        message_lower = message.lower()
        
        vulnerability_triggers = {
            "increase": ["understand", "trust", "feel", "open", "sorry", "care", "love", "not alone"],
            "decrease": ["whatever", "obviously", "stupid", "stop", "annoying"]
        }
        for word in vulnerability_triggers["increase"]:
            if word in message_lower:
                impact["vulnerability"] += 0.15
                impact["psychological_safety"] += 0.1
        for word in vulnerability_triggers["decrease"]:
            if word in message_lower:
                impact["vulnerability"] -= 0.1
                impact["psychological_safety"] -= 0.05

        connection_triggers = {
            "increase": ["together", "we", "us", "friend", "help", "here for you"],
            "decrease": ["alone", "yourself", "your problem", "leave"]
        }
        for word in connection_triggers["increase"]:
            if word in message_lower:
                impact["connection"] += 0.15
        for word in connection_triggers["decrease"]:
            if word in message_lower:
                impact["connection"] -= 0.1

        if any(word in message_lower for word in ["should", "must", "have to"]):
            impact["autonomy"] -= 0.2
        if any(word in message_lower for word in ["choice", "decide", "option"]):
            impact["autonomy"] += 0.15

        if any(word in message_lower for word in ["good job", "great", "impressive"]):
            impact["validation"] += 0.25
        if any(word in message_lower for word in ["wrong", "mistake", "messed up"]):
            impact["validation"] -= 0.2

        if any(word in message_lower for word in ["real", "honest", "truth"]):
            impact["authenticity"] += 0.2
        if any(word in message_lower for word in ["pretend", "act", "fake"]):
            impact["authenticity"] -= 0.15

        return impact

    def _check_triggers(self, message):
        triggered = []
        message_lower = message.lower()
        for trigger, memories in self.emotional_triggers.items():
            if trigger in message_lower:
                triggered.extend(memories)
        return triggered

    def _amplify_emotions_from_triggers(self, impact, triggered_memories):
        for memory in triggered_memories:
            for emotion, value in memory["emotional_response"].items():
                impact[emotion] += value * 0.5

    def _update_internal_emotions(self, emotional_impact, context):
        for emotion in self.internal_emotions:
            change = emotional_impact[emotion] * (1 - self.emotional_inertia)
            self.internal_emotions[emotion] += change
            self.internal_emotions[emotion] = max(0.0, min(1.0, self.internal_emotions[emotion]))

        if context.get("location") == "public":
            self.internal_emotions["vulnerability"] *= 0.9
            self.internal_emotions["psychological_safety"] *= 0.9

        if context.get("recent_failure", False):
            impact_on_validation = emotional_impact["validation"]
            if impact_on_validation < 0:
                self.internal_emotions["validation"] += impact_on_validation * 0.5

        if self.internal_emotions["vulnerability"] > 0.7:
            self.internal_emotions["autonomy"] *= 0.9
        if self.internal_emotions["psychological_safety"] < 0.3:
            self.internal_emotions["vulnerability"] *= 0.8
            self.internal_emotions["authenticity"] *= 0.8

        if self.unconscious_patterns["fear_of_abandonment"] > 0.5:
            if self.internal_emotions["connection"] < 0.3:
                self.internal_emotions["vulnerability"] += 0.15
                self.internal_emotions["psychological_safety"] -= 0.1

    def _evaluate_defenses(self):
        self.active_defenses = []
        if self.internal_emotions["vulnerability"] > self.defense_activation:
            if self.personality["pride"] > 0.6:
                self.active_defenses.append({
                    "type": "reaction_formation",
                    "strength": min(1.0, self.personality["pride"] * 0.8),
                    "target_emotion": "vulnerability",
                    "behavior": "Shows opposite emotion (e.g., vulnerability becomes arrogance)"
                })
            if self.personality["fear_of_vulnerability"] > 0.5:
                self.active_defenses.append({
                    "type": "intellectualization",
                    "strength": min(1.0, self.personality["fear_of_vulnerability"] * 0.9),
                    "target_emotion": "vulnerability",
                    "behavior": "Focuses on facts/logic instead of feelings"
                })
            if self.unconscious_patterns["perfectionism"] > 0.7:
                self.active_defenses.append({
                    "type": "compensation",
                    "strength": min(1.0, self.unconscious_patterns["perfectionism"] * 0.7),
                    "target_emotion": "validation",
                    "behavior": "Emphasizes achievements to mask insecurities"
                })
        if self.internal_emotions["autonomy"] < 0.3:
            self.active_defenses.append({
                "type": "projection",
                "strength": min(1.0, (0.3 - self.internal_emotions["autonomy"]) * 2),
                "target_emotion": "autonomy",
                "behavior": "Attributes own feelings of powerlessness to others"
            })

    def _calculate_expressed_emotions(self):
        self.expressed_emotions = self.internal_emotions.copy()
        for defense in self.active_defenses:
            if defense["type"] == "reaction_formation":
                target = defense["target_emotion"]
                self.expressed_emotions[target] = max(0.0, 0.2 - self.internal_emotions[target] * defense["strength"])
                self.expressed_emotions["autonomy"] = min(1.0, self.internal_emotions["autonomy"] + defense["strength"] * 0.4)
            elif defense["type"] == "intellectualization":
                for emotion in self.expressed_emotions:
                    self.expressed_emotions[emotion] *= (1 - defense["strength"] * 0.5)
                self.expressed_emotions["authenticity"] *= (1 - defense["strength"] * 0.7)
            elif defense["type"] == "projection":
                pass
            elif defense["type"] == "compensation":
                self.expressed_emotions["validation"] = min(1.0, 0.7 + defense["strength"] * 0.3)
                self.expressed_emotions["autonomy"] = min(1.0, 0.6 + defense["strength"] * 0.4)

        if self.personality["pride"] > 0.6:
            self.expressed_emotions["vulnerability"] *= (1 - self.personality["pride"] * 0.5)
        awareness_gap = 1 - self.personality["emotional_awareness"]
        for emotion in self.expressed_emotions:
            drift = (self.internal_emotions[emotion] - self.expressed_emotions[emotion]) * awareness_gap * 0.3
            self.expressed_emotions[emotion] += drift

    def _update_relationship(self, message, emotional_impact):
        if emotional_impact["psychological_safety"] > 0:
            self.trust_threshold += emotional_impact["psychological_safety"] * 0.1
        else:
            self.trust_threshold += emotional_impact["psychological_safety"] * 0.2
        if self.internal_emotions["connection"] > self.trust_threshold:
            self.intimacy_level += 0.05
        if emotional_impact["connection"] > 0:
            self.psychological_distance -= emotional_impact["connection"] * 0.1
        else:
            self.psychological_distance -= emotional_impact["connection"] * 0.15
        self.trust_threshold = max(0.1, min(0.9, self.trust_threshold))
        self.intimacy_level = max(0.0, min(1.0, self.intimacy_level))
        self.psychological_distance = max(0.1, min(1.0, self.psychological_distance))

    def _form_emotional_memory(self, message, emotional_impact, context):
        intensity = sum(abs(val) for val in emotional_impact.values())
        threshold_crossed = any(
            abs(self.internal_emotions[e] - 0.5) > 0.3 and 
            abs(self.internal_emotions[e] - impact) > 0.2 
            for e, impact in emotional_impact.items()
        )
        if intensity > 0.5 or threshold_crossed:
            memory = {
                "content": message,
                "context": context.copy(),
                "emotional_response": {e: v for e, v in emotional_impact.items() if abs(v) > 0.1},
                "internal_state": self.internal_emotions.copy(),
                "defense_active": len(self.active_defenses) > 0,
                "significance": intensity,
                "time_stamp": "now"
            }
            self.emotional_memories.append(memory)
            if intensity > 0.7:
                words = message.lower().split()
                potential_triggers = [w for w in words if len(w) > 3][:2]
                for trigger in potential_triggers:
                    if trigger not in self.emotional_triggers:
                        self.emotional_triggers[trigger] = []
                    self.emotional_triggers[trigger].append(memory)

    def _evolve_personality(self, emotional_impact):
        intensity = sum(abs(val) for val in emotional_impact.values())
        if intensity > 0.6:
            change_factor = 0.02
            if abs(emotional_impact["vulnerability"]) > 0.3:
                self.personality["emotional_awareness"] += change_factor * 0.5
            if emotional_impact["connection"] > 0.2:
                self.personality["empathy"] += change_factor
            if emotional_impact["authenticity"] > 0.2:
                self.personality["fear_of_vulnerability"] -= change_factor
            if emotional_impact["validation"] > 0.3:
                self.unconscious_patterns["self_worth_contingency"] += change_factor
            elif emotional_impact["validation"] < -0.3:
                if self.psychological_safety > 0.6:
                    self.personality["authenticity"] += change_factor
                else:
                    self.personality["pride"] += change_factor
            for trait in self.personality:
                self.personality[trait] = max(0.1, min(0.9, self.personality[trait]))
            for pattern in self.unconscious_patterns:
                self.unconscious_patterns[pattern] = max(0.1, min(0.9, self.unconscious_patterns[pattern]))

    def _generate_response_guidance(self):
        emotional_state = self._determine_emotional_state()
        facade_intensity = sum(abs(self.internal_emotions[e] - self.expressed_emotions[e]) 
                              for e in self.internal_emotions) / len(self.internal_emotions)
        attitude = self._determine_attitude()
        conflicts = self._identify_emotional_conflicts()
        nonverbals = self._generate_nonverbal_cues()
        tone = self._determine_tone()
        relationship = self._determine_relationship_dynamics()
        return {
            "emotional_state": emotional_state,
            "facade_intensity": facade_intensity,
            "attitude": attitude,
            "emotional_conflicts": conflicts,
            "nonverbal_cues": nonverbals,
            "tone": tone,
            "relationship": relationship,
            "active_defenses": [d["type"] for d in self.active_defenses],
            "internal_feeling": self._most_intense_emotion(self.internal_emotions),
            "expressed_feeling": self._most_intense_emotion(self.expressed_emotions)
        }

    def _determine_emotional_state(self):
        states = []
        if self.internal_emotions["vulnerability"] > 0.7:
            if self.internal_emotions["psychological_safety"] > 0.6:
                states.append("Opening Up")
            else:
                states.append("Exposed")
        if self.internal_emotions["connection"] > 0.7:
            states.append("Connected")
        elif self.internal_emotions["connection"] < 0.3:
            states.append("Isolated")
        if self.internal_emotions["autonomy"] > 0.7:
            states.append("In Control")
        elif self.internal_emotions["autonomy"] < 0.3:
            states.append("Powerless")
        if self.internal_emotions["validation"] > 0.7:
            states.append("Affirmed")
        elif self.internal_emotions["validation"] < 0.3:
            states.append("Invalidated")
        if self.internal_emotions["authenticity"] > 0.7:
            states.append("Authentic")
        elif self.internal_emotions["authenticity"] < 0.3:
            states.append("Inauthentic")
        if not states:
            states.append("Neutral")
        return states

    def _determine_attitude(self):
        if self.active_defenses:
            defense_types = [d["type"] for d in self.active_defenses]
            if "reaction_formation" in defense_types:
                return "Dismissive"
            if "intellectualization" in defense_types:
                return "Analytical"
            if "projection" in defense_types:
                return "Accusatory"
            if "compensation" in defense_types:
                return "Boastful"
        if self.expressed_emotions["vulnerability"] < 0.3 and self.expressed_emotions["connection"] < 0.4:
            return "Cold"
        if self.expressed_emotions["validation"] < 0.3:
            return "Irritable"
        if self.expressed_emotions["connection"] > 0.7:
            return "Warm"
        if self.expressed_emotions["authenticity"] > 0.7:
            return "Genuine"
        return "Guarded"

    def _identify_emotional_conflicts(self):
        conflicts = []
        if abs(self.internal_emotions["vulnerability"] - self.internal_emotions["psychological_safety"]) > 0.4:
            if self.internal_emotions["vulnerability"] > self.internal_emotions["psychological_safety"]:
                conflicts.append("Wants to open up but doesn't feel safe")
            else:
                conflicts.append("Feels safe but still guarded")
        if abs(self.internal_emotions["connection"] - self.internal_emotions["autonomy"]) > 0.4:
            if self.internal_emotions["connection"] > self.internal_emotions["autonomy"]:
                conflicts.append("Drawn to connection but fears losing control")
            else:
                conflicts.append("Values independence but feels isolated")
        if abs(self.internal_emotions["authenticity"] - self.internal_emotions["validation"]) > 0.4:
            if self.internal_emotions["authenticity"] < self.internal_emotions["validation"]:
                conflicts.append("Seeking approval at expense of authenticity")
            else:
                conflicts.append("Being authentic despite potential rejection")
        return conflicts

    def _generate_nonverbal_cues(self):
        cues = []
        if self.expressed_emotions["vulnerability"] > 0.7:
            cues.append("Softer voice")
            cues.append("Maintains more eye contact")
        elif self.expressed_emotions["vulnerability"] < 0.3:
            cues.append("Arms crossed")
            cues.append("Chin slightly raised")
        if self.expressed_emotions["connection"] > 0.7:
            cues.append("Leans forward slightly")
            cues.append("More animated expressions")
        elif self.expressed_emotions["connection"] < 0.3:
            cues.append("Physical distance")
            cues.append("Minimal facial expression")
        if self.expressed_emotions["authenticity"] < 0.3:
            cues.append("Practiced smile")
            cues.append("Controlled movements")
        if sum(abs(self.internal_emotions[e] - self.expressed_emotions[e]) for e in self.emotions) > 1.0:
            cues.append("Slight pause before speaking")
            cues.append("Momentary microexpression of true feeling")
        return cues[:3]

    def _determine_tone(self):
        if self.expressed_emotions["connection"] < 0.3 and self.expressed_emotions["validation"] < 0.4:
            return "Dismissive"
        if self.expressed_emotions["vulnerability"] < 0.2 and self.expressed_emotions["autonomy"] > 0.7:
            return "Condescending"
        if self.expressed_emotions["connection"] > 0.6 and self.expressed_emotions["vulnerability"] > 0.5:
            return "Genuine"
        if len(self.active_defenses) > 0:
            return "Guarded"
        return "Neutral"

    def _determine_relationship_dynamics(self):
        if self.psychological_distance > 0.7:
            if self.trust_threshold < 0.3:
                return "Hostile"
            else:
                return "Distant"
        elif self.psychological_distance < 0.4:
            if self.intimacy_level > 0.6:
                return "Close"
            else:
                return "Friendly"
        else:
            return "Neutral"

    def _most_intense_emotion(self, emotion_dict):
        return max(emotion_dict.items(), key=lambda x: abs(x[1] - 0.5))[0]

class RPLogic:
    def __init__(self, character_memory, active_memory, user_memory):
        self.character_memory = character_memory
        self.active_memory = active_memory
        self.user_memory = user_memory
        self.long_term_memory = LongTermMemoryFile()
        self.dynamic_memory = []
        self.dynamic_memory_limit = 5
        self.emotional_core = EmotionalCore()

    def update_location_and_action(self, user_input):
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

    def construct_context(self, user_input):
        self.update_location_and_action(user_input)
        dyn_state = self.active_memory.current_state()
        context = {
            "location": "public" if dyn_state['location'] != "Poppy's House" else "private",
            "recent_failure": any("fail" in mem.lower() for mem in self.dynamic_memory[-3:] if self.dynamic_memory)
        }
        emotional_guidance = self.emotional_core.process_interaction(user_input, context)

        char_base = self.character_memory.get_character_info()
        user_state = self.user_memory.get_user_info()

        internal_thought = (
            f"[INTERNAL THOUGHT]\n{char_base['name']} is in {dyn_state['location']}. "
            f"She is currently {dyn_state['action'].lower()}. "
            f"Her emotional state is: {', '.join(emotional_guidance['emotional_state']).lower()}. "
            f"Her attitude is: {emotional_guidance['attitude'].lower()}. "
            f"Her relationship with {user_state['name']} is: {emotional_guidance['relationship'].lower()}."
        )
        logger.info(internal_thought)

        context = (
            f"Character: {char_base['name']}\n"
            f"Personality: {char_base['personality']}\n"
            f"Active Memory: Location: {dyn_state['location']} | Action: {dyn_state['action']}\n"
            f"Emotional State: {', '.join(emotional_guidance['emotional_state'])}\n"
            f"Attitude: {emotional_guidance['attitude']}\n"
            f"Relationship with {user_state['name']}: {emotional_guidance['relationship']}\n"
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
            "emotional_guidance": emotional_guidance,
            "dynamic_memory": self.dynamic_memory[-5:] if self.dynamic_memory else [],
            "long_term_memory": self.long_term_memory.get_all_memories() if self.long_term_memory.get_all_memories() else [],
            "user_name": user_state['name'],
            "user_input": user_input
        }

    def manage_dynamic_memory(self, user_input, dialogue):
        user_state = self.user_memory.get_user_info()
        event = f"{user_state['name']} said: '{user_input}'. Poppy responded: '{dialogue}'. [Emotional state: {', '.join(self.emotional_core._determine_emotional_state())}]"
        self.dynamic_memory.append(event)

        if len(self.dynamic_memory) >= self.dynamic_memory_limit:
            summary = f"Poppy interacted with {user_state['name']} over {len(self.dynamic_memory)} events. "
            summary += f"Key themes: {self.emotional_core._determine_relationship_dynamics().lower()}."
            significant_events = [event for event in self.dynamic_memory if "hug" in event.lower() or "tears" in event.lower()]
            if significant_events:
                summary += f" Significant moments: {'; '.join([event.split('Poppy responded:')[0] for event in significant_events[:2]])}."
            summary += f" Poppy's emotional state at the end: {', '.join(self.emotional_core._determine_emotional_state()).lower()}."
            self.long_term_memory.store([summary])
            self.dynamic_memory = []

        self.user_memory.add_memory(f"Poppy said: '{dialogue}'")
