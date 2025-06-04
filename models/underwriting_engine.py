import os
import json
import openai
import re
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

class UnderwritingEngine:
    """
    Handles the conversation with users, extracting relevant information
    for insurance underwriting purposes.
    """
    
    def __init__(self):
        self.client_info = {}
        self.current_state = "greeting"
        # Simplified required fields, focusing on what's needed for qualification
        self.required_fields = [
            "name", "age", "health_conditions", "smoking_status", "coverage_amount", "coverage_type"
        ]
        
        # Initialize OpenAI if API key is available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            openai.api_key = openai_api_key
            self.llm = OpenAI(temperature=0.7)
            self.memory = ConversationBufferMemory()
            self.conversation = ConversationChain(
                llm=self.llm,
                memory=self.memory,
                verbose=False
            )
        else:
            print("Warning: OPENAI_API_KEY not found. Using fallback mode.")
            self.conversation = None
    
    def process_message(self, message, chat_history=None):
        """
        Process incoming messages, update client information,
        and determine the next step in the underwriting process.
        """
        # Update conversation history if provided
        if chat_history and self.conversation:
            for entry in chat_history:
                if entry.get('role') == 'user':
                    self.memory.chat_memory.add_user_message(entry.get('content', ''))
                elif entry.get('role') == 'assistant':
                    self.memory.chat_memory.add_ai_message(entry.get('content', ''))
        
        # Extract information from message
        self._extract_client_info(message)
        
        # Debug - print current client info
        print(f"Current client info: {json.dumps(self.client_info, indent=2, ensure_ascii=False)}")
        
        # Check if we have enough info to skip states
        if "name" in self.client_info and "age" in self.client_info and self.current_state == "greeting":
            print("Fast-tracking from greeting to collecting_policy_info")
            self.current_state = "collecting_policy_info"
        
        # Determine the next state based on current information
        self._update_state()
        
        # Generate response based on current state
        return self._generate_response(message)
    
    def _extract_client_info(self, message):
        """Extract client information from the message using NLP."""
        # Print the message for debugging
        print(f"Extracting info from message: {message}")
        
        # Extract name
        name_patterns = [
            r"(?:my name is|I am|I'm|name[:\s]+)\s*([A-Za-z]+)",
            r"([A-Za-z]+)(?:,|\s+)(?:\d+)(?:,|\s+)",  # Pattern like "Kyle, 25, developer"
            r"name is ([A-Za-z]+)"
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, message, re.IGNORECASE)
            if name_match:
                self.client_info["name"] = name_match.group(1).strip()
                print(f"Extracted name: {self.client_info['name']}")
                break
        
        # Extract age
        age_patterns = [
            r"(?:I am|I'm|age[:\s]+)\s*(\d+)",
            r"(\d+)(?:,|\s+years old|\s+year old|\s+years|\s+year)",
            r"(?:I am|I'm)\s+(?:a\s+)?(\d+)(?:\s+years?)?(?:\s+old)?",
            r"(?:my name is|name is).*?(?:I am|I'm)?\s+(\d+)",
            r"(?:,|\s+)(\d+)(?:,|\s+|\.)"  # Pattern like "Kyle, 25, " or "I am Kyle. 25. I"
        ]
        
        for pattern in age_patterns:
            age_match = re.search(pattern, message, re.IGNORECASE)
            if age_match:
                age_text = age_match.group(1)
                if age_text.isdigit():
                    self.client_info["age"] = int(age_text)
                    print(f"Extracted age: {self.client_info['age']}")
                break
        
        # Extract policy type directly
        policy_keywords = {
            "whole life": "whole_life",
            "whole": "whole_life",
            "term life": "term_life", 
            "term": "term_life",
            "universal life": "universal_life",
            "universal": "universal_life",
            "final expense": "final_expense"
        }
        
        for keyword, policy_type in policy_keywords.items():
            if keyword in message.lower():
                self.client_info["coverage_type"] = policy_type
                print(f"Extracted policy type: {self.client_info['coverage_type']}")
                break
        
        # Extract health conditions
        if any(x in message.lower() for x in ["health", "medical", "condition", "issue", "problem", "diagnosis"]):
            if any(x in message.lower() for x in ["no health", "no issues", "healthy", "good health", "no medical"]):
                self.client_info["health_conditions"] = []
                print("Extracted health: No conditions")
            elif "health_conditions" not in self.client_info:
                # Extract specific conditions if mentioned
                conditions = []
                if "diabetes" in message.lower():
                    conditions.append("diabetes")
                if "cancer" in message.lower():
                    conditions.append("cancer")
                if "heart" in message.lower() or "cardiac" in message.lower():
                    conditions.append("heart condition")
                if "blood pressure" in message.lower() or "hypertension" in message.lower():
                    conditions.append("hypertension")
                
                if conditions:
                    self.client_info["health_conditions"] = conditions
                    print(f"Extracted health conditions: {conditions}")
                else:
                    # If health is mentioned but no specific conditions
                    self.client_info["health_conditions"] = []
                    print("Extracted health: Default to no conditions")
        
        # Extract smoking status
        if "smoke" in message.lower() or "smoking" in message.lower() or "tobacco" in message.lower():
            if any(x in message.lower() for x in ["don't smoke", "do not smoke", "non-smoker", "nonsmoker", "non smoker", "no tobacco"]):
                self.client_info["smoking_status"] = "non-smoker"
                print("Extracted smoking status: non-smoker")
            else:
                self.client_info["smoking_status"] = "smoker"
                print("Extracted smoking status: smoker")
        
        # Extract coverage amount
        coverage_patterns = [
            r"(?:coverage|policy|amount)[:\s]+[$]?(\d{1,3}(?:,\d{3})*|\d+)[k]?",
            r"[$]?(\d{1,3}(?:,\d{3})*|\d+)[k]? (?:coverage|policy|amount)",
            r"[$]?(\d{1,3}(?:,\d{3})*|\d+)[k]?(?:\s+dollars|\s+USD)"
        ]
        
        for pattern in coverage_patterns:
            coverage_match = re.search(pattern, message, re.IGNORECASE)
            if coverage_match:
                coverage_text = coverage_match.group(1).replace(',', '')
                # Check if the amount has a 'k' suffix (for thousands)
                if coverage_match.group(0).lower().endswith('k'):
                    coverage_amount = int(coverage_text) * 1000
                else:
                    coverage_amount = int(coverage_text)
                
                self.client_info["coverage_amount"] = coverage_amount
                print(f"Extracted coverage amount: {coverage_amount}")
                break
    
    def _update_state(self):
        """Update the conversation state based on collected information."""
        # Print current state before update
        print(f"Current state before update: {self.current_state}")
        
        # If health is described as "healthy" or "no issues", automatically set non-smoker
        # unless explicitly stated otherwise
        if "health_conditions" in self.client_info and not self.client_info["health_conditions"]:
            if "smoking_status" not in self.client_info:
                self.client_info["smoking_status"] = "non-smoker"
        
        # Handle state transitions more intelligently
        
        # If we're in greeting and have both name and age, skip to policy info
        if "name" in self.client_info and "age" in self.client_info:
            if self.current_state == "greeting" or self.current_state == "collecting_basic_info":
                self.current_state = "collecting_policy_info"
                print(f"Updated state to: {self.current_state} (fast-track)")
                
        # If we're in policy info and have coverage type, ask about health
        if "coverage_type" in self.client_info and "name" in self.client_info and "age" in self.client_info:
            if self.current_state == "collecting_policy_info":
                # If we also have coverage amount, definitely move to health
                if "coverage_amount" in self.client_info:
                    self.current_state = "collecting_health_info"
                    print(f"Updated state to: {self.current_state}")
        
        # If we have health info, move to assessment
        if "health_conditions" in self.client_info and "coverage_type" in self.client_info:
            if self.current_state == "collecting_health_info":
                self.current_state = "providing_assessment"
                print(f"Updated state to: {self.current_state}")
        
        # If we have basic info and health but not policy, switch to policy
        if "name" in self.client_info and "age" in self.client_info and "health_conditions" in self.client_info and "coverage_type" not in self.client_info:
            if self.current_state == "collecting_health_info":
                self.current_state = "collecting_policy_info"
                print(f"Updated state to: {self.current_state}")
        
        # Default transitions for initial states
        if self.current_state == "greeting":
            self.current_state = "collecting_basic_info"
            print(f"Updated state to: {self.current_state}")
            
        # Print current state after update
        print(f"Final state: {self.current_state}")
    
    def _generate_response(self, message):
        """Generate a response based on the current state and user message."""
        # If we have OpenAI integration, use it for responses
        if self.conversation:
            prompt = self._create_prompt(message)
            return self.conversation.predict(input=prompt)
        
        # Get client name for personalization
        client_name = self.client_info.get("name", "there")
        
        # Fallback responses - direct and to the point
        if self.current_state == "greeting":
            return "Hello! What's your name and age?"
        
        elif self.current_state == "collecting_basic_info":
            if "name" in self.client_info:
                if "age" not in self.client_info:
                    return f"What is your age?"
                else:
                    return f"What type of life insurance policy and coverage amount are you looking for?"
            else:
                return "I need your name and age to get started."
        
        elif self.current_state == "collecting_policy_info":
            policy_type = self.client_info.get("coverage_type", "")
            if policy_type:
                policy_name = policy_type.replace("_", " ")
                if "coverage_amount" in self.client_info:
                    amount = self.client_info["coverage_amount"]
                    
                    # Now recommend policies based on age, type and amount
                    age = self.client_info.get("age", 0)
                    
                    # Simplified company selection - ONLY from companies.json
                    recommended_companies = []
                    if policy_type == "whole_life":
                        if age < 30:
                            recommended_companies = ["Foresters Financial", "SBLI"]
                            if amount <= 25000:
                                recommended_companies.append("Corebridge Financial")
                        elif age < 50:
                            recommended_companies = ["Legal & General America", "SBLI"]
                        else:
                            recommended_companies = ["Liberty Bankers Life", "Royal Neighbors of America"]
                    elif policy_type == "term_life":
                        recommended_companies = ["Legal & General America", "SBLI", "American General Life"]
                    elif policy_type == "final_expense":
                        recommended_companies = ["Royal Neighbors of America", "Dignity Solutions", "United Home Life"]
                    
                    # If no specific recommendations, include default options
                    if not recommended_companies:
                        recommended_companies = ["SBLI", "Foresters Financial", "Liberty Bankers Life"]
                    
                    return f"Based on your age ({age}) and coverage amount (${amount:,}), the best options are from {', '.join(recommended_companies)}. Any health conditions I should know about?"
                else:
                    return f"What coverage amount are you looking for?"
            else:
                return f"What type of life insurance policy and coverage amount do you need?"
        
        elif self.current_state == "collecting_health_info":
            if "health_conditions" in self.client_info:
                if not self.client_info["health_conditions"]:
                    # Build a more direct recommendation based on available companies
                    age = self.client_info.get("age", 0)
                    policy_type = self.client_info.get("coverage_type", "").replace("_", " ")
                    amount = self.client_info.get("coverage_amount", 0)
                    
                    if policy_type == "whole life" and age < 30:
                        return f"With no health issues at age {age}, you qualify for Preferred rates on a ${amount:,} {policy_type} policy from Foresters Financial at $45/month or SBLI at $48/month. Should I proceed with an application?"
                    elif policy_type == "whole life":
                        return f"With no health issues at age {age}, you qualify for Preferred rates on a ${amount:,} {policy_type} policy. The best rate is from SBLI at $62/month. Should I proceed with an application?"
                    else:
                        return f"With no health issues, you qualify for the best rates. The most competitive option is from Legal & General America. Would you like to apply?"
                else:
                    conditions = ", ".join(self.client_info["health_conditions"])
                    return f"With {conditions}, you'd likely qualify for Standard rates with Liberty Bankers Life or Royal Neighbors of America. Would you like details on their policies?"
            else:
                return f"Any health conditions I should know about?"
        
        elif self.current_state == "providing_assessment":
            # Simplified assessment with direct policy recommendations
            policy_type = self.client_info.get("coverage_type", "").replace("_", " ")
            amount = self.client_info.get("coverage_amount", 0)
            health_conditions = self.client_info.get("health_conditions", [])
            age = self.client_info.get("age", 0)
            
            if not health_conditions:
                if age < 30 and amount <= 25000:
                    return f"Best option: Corebridge Financial, ${amount:,} coverage at $42/month. Second best: Foresters Financial at $45/month. Ready to apply?"
                elif age < 50:
                    return f"Best option: SBLI, ${amount:,} coverage at $58/month with Preferred rates. Ready to apply?"
                else:
                    return f"Best option: Liberty Bankers Life, ${amount:,} coverage at $72/month. Second best: Royal Neighbors of America at $76/month. Ready to apply?"
            else:
                if any(c in ["cancer", "heart condition"] for c in health_conditions):
                    return f"With your health history, Liberty Bankers Life offers the best coverage at Standard rates: ${amount:,} for $85/month. Ready to apply?"
                else:
                    return f"With your health history, you qualify for SBLI at Standard rates: ${amount:,} for $68/month. Ready to apply?"
        
        return f"What else do you need to know about life insurance options?"
    
    def _create_prompt(self, message):
        """Create a prompt for the AI based on current state and client info."""
        if self.current_state == "greeting":
            return f"You are a direct, no-nonsense life insurance underwriting assistant. The user message is: '{message}'. Give a short greeting and ask for name and age only. Be extremely concise - no more than 10 words if possible."
        
        context = f"Current client information: {json.dumps(self.client_info, indent=2, ensure_ascii=False)}\n"
        context += f"Current state: {self.current_state}\n"
        context += f"User message: {message}\n\n"
        context += "IMPORTANT: You are a life insurance assistant. Be extremely direct and concise. No small talk, pleasantries, or unnecessary words. Stick to life insurance only.\n\n"
        
        # Add allowed companies
        context += "CRITICAL: ONLY recommend from these insurance companies: SBLI, Foresters Financial, Royal Neighbors of America, "
        context += "Legal & General America, Liberty Bankers Life, Corebridge Financial, American General Life, "
        context += "Kansas City Life, Dignity Solutions, Ameritas, American Home Life, United Home Life.\n\n"
        
        if self.current_state == "collecting_basic_info":
            context += "Ask for the client's name and age in as few words as possible. "
            context += "Once you have those, directly ask what type of life insurance and coverage amount they need."
        
        elif self.current_state == "collecting_policy_info":
            context += "Get policy type and coverage amount directly. "
            context += "Once you have this info, recommend specific companies from our allowed list based on age and policy type, then ask about health conditions."
        
        elif self.current_state == "collecting_health_info":
            context += "Ask about health conditions directly. "
            context += "Once you have this info, recommend specific policies with exact pricing from our allowed companies only."
        
        elif self.current_state == "providing_assessment":
            context += "Provide a direct assessment with specific companies, policy prices, and coverage details. "
            context += "Be extremely specific and direct. Avoid phrases like 'I can' or 'I would'. Just state the facts and ask if they want to apply."
        
        return context 