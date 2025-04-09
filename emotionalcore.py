class EmotionalCore:
    def __init__(self):
        # Core emotional dimensions (using more nuanced dimensions than typical models)
        self.emotions = {
            "vulnerability": 0.2,     # Feeling exposed/protected
            "connection": 0.1,        # Feeling close/distant
            "autonomy": 0.8,          # Feeling in control/controlled
            "validation": 0.3,        # Feeling affirmed/rejected
            "authenticity": 0.4,      # Feeling true/false to self
            "psychological_safety": 0.2  # Environment feels safe/threatening
        }
        
        # Separate internal vs. expressed emotions (what's felt vs. shown)
        self.internal_emotions = self.emotions.copy()
        self.expressed_emotions = {k: v for k, v in self.emotions.items()}
        
        # Defense mechanism strength (dynamically adjusts based on vulnerability)
        self.defense_activation = 0.7  # Threshold for activating defenses
        self.active_defenses = []
        
        # Memory with emotional context
        self.emotional_memories = []
        self.emotional_triggers = {}  # Words/phrases that trigger emotional responses
        
        # Relationship tracking
        self.trust_threshold = 0.5
        self.intimacy_level = 0.1
        self.psychological_distance = 0.9
        
        # Personality baseline (Poppy's starting traits)
        self.personality = {
            "pride": 0.8,
            "fear_of_vulnerability": 0.7, 
            "need_for_control": 0.8,
            "emotional_awareness": 0.4,  # How aware is she of her own emotions
            "empathy": 0.3,
            "authenticity": 0.4
        }
        
        # Emotional stability and volatility
        self.emotional_inertia = 0.7  # How resistant emotions are to change (0-1)
        self.emotional_volatility = 0.4  # How extreme emotional responses can be
        
        # Unconscious patterns (things Poppy doesn't realize about herself)
        self.unconscious_patterns = {
            "fear_of_abandonment": 0.6,
            "perfectionism": 0.8,
            "self_worth_contingency": 0.7  # Self-worth tied to achievement/status
        }
        
    def process_interaction(self, message, context):
        """Process user interaction and generate authentic emotional response"""
        # Step 1: Analyze the message for emotional content
        emotional_impact = self._analyze_emotional_content(message)
        
        # Step 2: Check for emotional triggers from past experiences
        triggered_memories = self._check_triggers(message)
        if triggered_memories:
            # Enhance emotional impact based on triggered memories
            self._amplify_emotions_from_triggers(emotional_impact, triggered_memories)
        
        # Step 3: Process internal emotional response (what Poppy actually feels)
        self._update_internal_emotions(emotional_impact, context)
        
        # Step 4: Determine defense mechanisms if needed
        self._evaluate_defenses()
        
        # Step 5: Calculate expressed emotions (what Poppy shows)
        self._calculate_expressed_emotions()
        
        # Step 6: Update relationship dynamics
        self._update_relationship(message, emotional_impact)
        
        # Step 7: Form new emotional memories
        self._form_emotional_memory(message, emotional_impact, context)
        
        # Step 8: Update personality gradually based on significant experiences
        self._evolve_personality(emotional_impact)
        
        # Step 9: Generate response guidance for dialogue generator
        return self._generate_response_guidance()
    
    def _analyze_emotional_content(self, message):
        """Analyze the emotional impact of a message with psychological depth"""
        # Initialize impact values
        impact = {emotion: 0.0 for emotion in self.emotions}
        
        # Basic keyword analysis (would be much more sophisticated in practice)
        message_lower = message.lower()
        
        # Impact on vulnerability
        vulnerability_triggers = {
            "increase": ["understand", "trust", "feel", "open", "sorry", "care"],
            "decrease": ["whatever", "obviously", "stupid", "stop"]
        }
        for word in vulnerability_triggers["increase"]:
            if word in message_lower:
                impact["vulnerability"] += 0.15
                impact["psychological_safety"] += 0.1
                
        for word in vulnerability_triggers["decrease"]:
            if word in message_lower:
                impact["vulnerability"] -= 0.1
                impact["psychological_safety"] -= 0.05
        
        # Impact on connection
        connection_triggers = {
            "increase": ["together", "we", "us", "friend", "help"],
            "decrease": ["alone", "yourself", "your problem"]
        }
        for word in connection_triggers["increase"]:
            if word in message_lower:
                impact["connection"] += 0.15
                
        for word in connection_triggers["decrease"]:
            if word in message_lower:
                impact["connection"] -= 0.1
        
        # Impact on autonomy (feeling of control)
        if any(word in message_lower for word in ["should", "must", "have to"]):
            impact["autonomy"] -= 0.2
            
        if any(word in message_lower for word in ["choice", "decide", "option"]):
            impact["autonomy"] += 0.15
        
        # Impact on validation
        if any(word in message_lower for word in ["good job", "great", "impressive"]):
            impact["validation"] += 0.25
            
        if any(word in message_lower for word in ["wrong", "mistake", "messed up"]):
            impact["validation"] -= 0.2
        
        # Impact on authenticity
        if any(word in message_lower for word in ["real", "honest", "truth"]):
            impact["authenticity"] += 0.2
            
        if any(word in message_lower for word in ["pretend", "act", "fake"]):
            impact["authenticity"] -= 0.15
            
        return impact
    
    def _check_triggers(self, message):
        """Check if message contains emotional triggers from past experiences"""
        triggered = []
        message_lower = message.lower()
        
        for trigger, memories in self.emotional_triggers.items():
            if trigger in message_lower:
                triggered.extend(memories)
                
        return triggered
    
    def _amplify_emotions_from_triggers(self, impact, triggered_memories):
        """Amplify emotional impact based on triggered memories"""
        for memory in triggered_memories:
            # Extract emotion from memory and amplify current impact
            for emotion, value in memory["emotional_response"].items():
                impact[emotion] += value * 0.5  # Dampened effect from memory
    
    def _update_internal_emotions(self, emotional_impact, context):
        """Update internal emotional state based on impact and context"""
        # Apply emotional inertia - emotions resist change
        for emotion in self.internal_emotions:
            # Calculate change magnitude with inertia
            change = emotional_impact[emotion] * (1 - self.emotional_inertia)
            
            # Apply change
            self.internal_emotions[emotion] += change
            
            # Constrain within valid range
            self.internal_emotions[emotion] = max(0.0, min(1.0, self.internal_emotions[emotion]))
        
        # Context modifiers
        if context.get("location") == "public":
            # In public, vulnerability decreases
            self.internal_emotions["vulnerability"] *= 0.9
            self.internal_emotions["psychological_safety"] *= 0.9
        
        if context.get("recent_failure", False):
            # After failure, validation sensitivity increases
            impact_on_validation = emotional_impact["validation"]
            if impact_on_validation < 0:
                # Negative validation hits harder after failure
                self.internal_emotions["validation"] += impact_on_validation * 0.5
        
        # Emotional interactions (emotions affect each other)
        if self.internal_emotions["vulnerability"] > 0.7:
            # High vulnerability reduces autonomy
            self.internal_emotions["autonomy"] *= 0.9
        
        if self.internal_emotions["psychological_safety"] < 0.3:
            # Low safety reduces vulnerability and authenticity
            self.internal_emotions["vulnerability"] *= 0.8
            self.internal_emotions["authenticity"] *= 0.8
            
        # Unconscious pattern effects
        if self.unconscious_patterns["fear_of_abandonment"] > 0.5:
            if self.internal_emotions["connection"] < 0.3:
                # Low connection triggers abandonment fear
                self.internal_emotions["vulnerability"] += 0.15
                self.internal_emotions["psychological_safety"] -= 0.1
    
    def _evaluate_defenses(self):
        """Evaluate and activate psychological defense mechanisms"""
        self.active_defenses = []
        
        # Check vulnerability threshold
        if self.internal_emotions["vulnerability"] > self.defense_activation:
            # Determine which defenses activate based on personality and context
            
            if self.personality["pride"] > 0.6:
                # High pride activates denial and reaction formation
                self.active_defenses.append({
                    "type": "reaction_formation",
                    "strength": min(1.0, self.personality["pride"] * 0.8),
                    "target_emotion": "vulnerability",
                    "behavior": "Shows opposite emotion (e.g., vulnerability becomes arrogance)"
                })
            
            if self.personality["fear_of_vulnerability"] > 0.5:
                # Fear of vulnerability activates intellectualization
                self.active_defenses.append({
                    "type": "intellectualization",
                    "strength": min(1.0, self.personality["fear_of_vulnerability"] * 0.9),
                    "target_emotion": "vulnerability",
                    "behavior": "Focuses on facts/logic instead of feelings"
                })
            
            if self.unconscious_patterns["perfectionism"] > 0.7:
                # Perfectionism activates compensation
                self.active_defenses.append({
                    "type": "compensation",
                    "strength": min(1.0, self.unconscious_patterns["perfectionism"] * 0.7),
                    "target_emotion": "validation",
                    "behavior": "Emphasizes achievements to mask insecurities"
                })
        
        # Low autonomy can trigger projection
        if self.internal_emotions["autonomy"] < 0.3:
            self.active_defenses.append({
                "type": "projection",
                "strength": min(1.0, (0.3 - self.internal_emotions["autonomy"]) * 2),
                "target_emotion": "autonomy",
                "behavior": "Attributes own feelings of powerlessness to others"
            })
    
    def _calculate_expressed_emotions(self):
        """Calculate emotions that are expressed based on internal state and defenses"""
        # Start with copying internal emotions
        self.expressed_emotions = self.internal_emotions.copy()
        
        # Apply defense mechanisms to modify expressed emotions
        for defense in self.active_defenses:
            if defense["type"] == "reaction_formation":
                # Show opposite of vulnerable emotions
                target = defense["target_emotion"]
                self.expressed_emotions[target] = max(0.0, 0.2 - self.internal_emotions[target] * defense["strength"])
                
                # Increase displayed autonomy to compensate
                self.expressed_emotions["autonomy"] = min(1.0, self.internal_emotions["autonomy"] + defense["strength"] * 0.4)
            
            elif defense["type"] == "intellectualization":
                # Reduce emotional expression overall
                for emotion in self.expressed_emotions:
                    self.expressed_emotions[emotion] *= (1 - defense["strength"] * 0.5)
                
                # But authenticity drops most significantly
                self.expressed_emotions["authenticity"] *= (1 - defense["strength"] * 0.7)
            
            elif defense["type"] == "projection":
                # Minimal direct effect on expressed emotions
                # (This would affect dialogue content more than emotional display)
                pass
            
            elif defense["type"] == "compensation":
                # Increase displayed confidence/control
                self.expressed_emotions["validation"] = min(1.0, 0.7 + defense["strength"] * 0.3)
                self.expressed_emotions["autonomy"] = min(1.0, 0.6 + defense["strength"] * 0.4)
        
        # Personality always influences expression
        if self.personality["pride"] > 0.6:
            # High pride minimizes expression of vulnerability
            self.expressed_emotions["vulnerability"] *= (1 - self.personality["pride"] * 0.5)
        
        # Self-awareness affects how accurately emotions are expressed
        awareness_gap = 1 - self.personality["emotional_awareness"]
        for emotion in self.expressed_emotions:
            # Low awareness creates larger gap between felt and expressed emotions
            drift = (self.internal_emotions[emotion] - self.expressed_emotions[emotion]) * awareness_gap * 0.3
            self.expressed_emotions[emotion] += drift
    
    def _update_relationship(self, message, emotional_impact):
        """Update relationship dynamics based on interaction"""
        # Trust changes
        if emotional_impact["psychological_safety"] > 0:
            self.trust_threshold += emotional_impact["psychological_safety"] * 0.1
        else:
            # Negative impacts hurt trust more than positive ones build it
            self.trust_threshold += emotional_impact["psychological_safety"] * 0.2
        
        # Intimacy changes
        if self.internal_emotions["connection"] > self.trust_threshold:
            # Connection above trust threshold increases intimacy
            self.intimacy_level += 0.05
        
        # Psychological distance changes
        if emotional_impact["connection"] > 0:
            self.psychological_distance -= emotional_impact["connection"] * 0.1
        else:
            self.psychological_distance -= emotional_impact["connection"] * 0.15
        
        # Constrain values to valid range
        self.trust_threshold = max(0.1, min(0.9, self.trust_threshold))
        self.intimacy_level = max(0.0, min(1.0, self.intimacy_level))
        self.psychological_distance = max(0.1, min(1.0, self.psychological_distance))
    
    def _form_emotional_memory(self, message, emotional_impact, context):
        """Form emotional memory from significant interactions"""
        # Calculate overall emotional intensity
        intensity = sum(abs(val) for val in emotional_impact.values())
        
        # Only store significant memories (high intensity or crossing thresholds)
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
                "time_stamp": "now"  # Would be actual timestamp
            }
            
            self.emotional_memories.append(memory)
            
            # Check if this should become an emotional trigger
            if intensity > 0.7:
                # Extract key phrases that might trigger this memory
                words = message.lower().split()
                potential_triggers = [w for w in words if len(w) > 3][:2]  # Simple approach
                
                for trigger in potential_triggers:
                    if trigger not in self.emotional_triggers:
                        self.emotional_triggers[trigger] = []
                    self.emotional_triggers[trigger].append(memory)
    
    def _evolve_personality(self, emotional_impact):
        """Gradually evolve personality based on emotional experiences"""
        # Significant emotional experiences can shift personality traits
        intensity = sum(abs(val) for val in emotional_impact.values())
        
        if intensity > 0.6:
            # High intensity experiences have more impact
            change_factor = 0.02  # Small incremental changes
            
            # Vulnerability experiences increase emotional awareness
            if abs(emotional_impact["vulnerability"]) > 0.3:
                self.personality["emotional_awareness"] += change_factor * 0.5
            
            # Connection experiences increase empathy
            if emotional_impact["connection"] > 0.2:
                self.personality["empathy"] += change_factor
            
            # Authenticity experiences decrease fear of vulnerability
            if emotional_impact["authenticity"] > 0.2:
                self.personality["fear_of_vulnerability"] -= change_factor
            
            # Validation experiences affect pride and self-worth
            if emotional_impact["validation"] > 0.3:
                # Positive validation reinforces contingent self-worth
                self.unconscious_patterns["self_worth_contingency"] += change_factor
            elif emotional_impact["validation"] < -0.3:
                # Negative validation can either increase defenses or lead to growth
                if self.psychological_safety > 0.6:
                    # In safe environment, can lead to growth
                    self.personality["authenticity"] += change_factor
                else:
                    # In unsafe environment, reinforces defenses
                    self.personality["pride"] += change_factor
            
            # Constrain values
            for trait in self.personality:
                self.personality[trait] = max(0.1, min(0.9, self.personality[trait]))
                
            for pattern in self.unconscious_patterns:
                self.unconscious_patterns[pattern] = max(0.1, min(0.9, self.unconscious_patterns[pattern]))
    
    def _generate_response_guidance(self):
        """Generate guidance for the dialogue generator based on emotional state"""
        # Create a higher-level emotional state description
        emotional_state = self._determine_emotional_state()
        
        # Calculate facade intensity (gap between internal and expressed)
        facade_intensity = sum(abs(self.internal_emotions[e] - self.expressed_emotions[e]) 
                              for e in self.internal_emotions) / len(self.internal_emotions)
        
        # Determine attitude based on emotional state and defenses
        attitude = self._determine_attitude()
        
        # Identify emotional conflicts (mixed feelings)
        conflicts = self._identify_emotional_conflicts()
        
        # Generate nonverbal cues based on emotional state
        nonverbals = self._generate_nonverbal_cues()
        
        # Choose tone based on expressed emotions
        tone = self._determine_tone()
        
        # Relationship dynamics
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
        """Determine overall emotional state from individual emotions"""
        # Map internal emotions to broader emotional states
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
        """Determine attitude based on emotional state and defenses"""
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
                
        # No active defenses, base on emotions
        if self.expressed_emotions["vulnerability"] < 0.3 and self.expressed_emotions["connection"] < 0.4:
            return "Cold"
        if self.expressed_emotions["validation"] < 0.3:
            return "Irritable"
        if self.expressed_emotions["connection"] > 0.7:
            return "Warm"
        if self.expressed_emotions["authenticity"] > 0.7:
            return "Genuine"
            
        # Default
        return "Guarded"
    
    def _identify_emotional_conflicts(self):
        """Identify internal emotional conflicts (mixed feelings)"""
        conflicts = []
        
        # Vulnerability vs Safety
        if abs(self.internal_emotions["vulnerability"] - self.internal_emotions["psychological_safety"]) > 0.4:
            if self.internal_emotions["vulnerability"] > self.internal_emotions["psychological_safety"]:
                conflicts.append("Wants to open up but doesn't feel safe")
            else:
                conflicts.append("Feels safe but still guarded")
                
        # Connection vs Autonomy
        if abs(self.internal_emotions["connection"] - self.internal_emotions["autonomy"]) > 0.4:
            if self.internal_emotions["connection"] > self.internal_emotions["autonomy"]:
                conflicts.append("Drawn to connection but fears losing control")
            else:
                conflicts.append("Values independence but feels isolated")
                
        # Authenticity vs Validation
        if abs(self.internal_emotions["authenticity"] - self.internal_emotions["validation"]) > 0.4:
            if self.internal_emotions["authenticity"] < self.internal_emotions["validation"]:
                conflicts.append("Seeking approval at expense of authenticity")
            else:
                conflicts.append("Being authentic despite potential rejection")
                
        return conflicts
    
    def _generate_nonverbal_cues(self):
        """Generate nonverbal cues based on emotional state"""
        cues = []
        
        # Vulnerability cues
        if self.expressed_emotions["vulnerability"] > 0.7:
            cues.append("Softer voice")
            cues.append("Maintains more eye contact")
        elif self.expressed_emotions["vulnerability"] < 0.3:
            cues.append("Arms crossed")
            cues.append("Chin slightly raised")
            
        # Connection cues
        if self.expressed_emotions["connection"] > 0.7:
            cues.append("Leans forward slightly")
            cues.append("More animated expressions")
        elif self.expressed_emotions["connection"] < 0.3:
            cues.append("Physical distance")
            cues.append("Minimal facial expression")
            
        # Authenticity cues
        if self.expressed_emotions["authenticity"] < 0.3:
            cues.append("Practiced smile")
            cues.append("Controlled movements")
            
        # Internal vs External conflict cues
        if sum(abs(self.internal_emotions[e] - self.expressed_emotions[e]) for e in self.emotions) > 1.0:
            cues.append("Slight pause before speaking")
            cues.append("Momentary microexpression of true feeling")
            
        return cues[:3]  # Limit to top 3 cues
    
    def _determine_tone(self):
        """Determine verbal tone based on expressed emotions"""
        if self.expressed_emotions["connection"] < 0.3 and self.expressed_emotions["validation"] < 0.4:
            return "Dismissive"
            
        if self.expressed_emotions["vulnerability"] < 0.2 and self.expressed_emotions["autonomy"] > 0.7:
            return "Condescending"
            
        if self.expressed_emotions["connection"] > 0.6 and self.expressed_emotions["vulnerability"] > 0.5:
            return "Genuine"
            
        if len(self.active_defenses) > 0:
            return "Guarded"
            
        # Default
        return "Neutral"
    
    def _determine_relationship_dynamics(self):
        """Determine relationship characteristics"""
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
        """Find the most intensely felt emotion"""
        return max(emotion_dict.items(), key=lambda x: abs(x[1] - 0.5))[0]
