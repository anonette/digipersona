import openai
import time
import json
from typing import Dict, Any, Optional
from config.settings import Settings

class GPTClient:
    """OpenAI GPT-4o client for persona responses"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.last_request_time = 0
        self.request_count = 0
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < (1.0 / Settings.REQUESTS_PER_SECOND):
            sleep_time = (1.0 / Settings.REQUESTS_PER_SECOND) - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request_with_retry(self, messages: list, max_tokens: int = None) -> str:
        """Make API request with retry logic"""
        max_tokens = max_tokens or Settings.MAX_TOKENS
        
        for attempt in range(Settings.MAX_RETRIES):
            try:
                self._rate_limit()
                
                response = self.client.chat.completions.create(
                    model=Settings.OPENAI_MODEL,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=Settings.TEMPERATURE
                )
                
                return response.choices[0].message.content.strip()
                
            except openai.RateLimitError:
                if attempt < Settings.MAX_RETRIES - 1:
                    wait_time = Settings.RETRY_DELAY * (2 ** attempt)
                    print(f"Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
            except openai.APIError as e:
                if attempt < Settings.MAX_RETRIES - 1:
                    wait_time = Settings.RETRY_DELAY * (2 ** attempt)
                    print(f"API error: {e}, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                print(f"Unexpected error: {e}")
                if attempt < Settings.MAX_RETRIES - 1:
                    time.sleep(Settings.RETRY_DELAY)
                else:
                    raise
        
        raise Exception("Max retries exceeded")
    
    def get_persona_response(self, persona_context: str, question: Dict[str, Any]) -> str:
        """Get persona response to a survey question"""
        
        # Build the prompt based on question type
        question_prompt = self._build_question_prompt(question)
        
        messages = [
            {
                "role": "system",
                "content": persona_context
            },
            {
                "role": "user", 
                "content": question_prompt
            }
        ]
        
        response = self._make_request_with_retry(messages)
        
        # Validate and clean response based on question type
        return self._validate_response(response, question)
    
    def _build_question_prompt(self, question: Dict[str, Any]) -> str:
        """Build question-specific prompt"""
        question_text = question["text"]
        question_type = question["type"]
        
        prompt = f"Question: {question_text}\n\n"
        
        if question_type == "scale":
            options = question.get("options", ["1", "2", "3", "4", "5"])
            prompt += f"Rate on a scale from {options[0]} to {options[-1]}.\n"
            prompt += "Respond with only the number."
            
        elif question_type == "multiple choice":
            options = question.get("options", [])
            prompt += "Choose one of the following options:\n"
            for i, option in enumerate(options, 1):
                prompt += f"{i}. {option}\n"
            prompt += "Respond with only the option text (not the number)."
            
        elif question_type == "checkbox":
            options = question.get("options", [])
            prompt += "Select all that apply from the following options:\n"
            for i, option in enumerate(options, 1):
                prompt += f"{i}. {option}\n"
            prompt += "Respond with the selected option texts separated by commas."
            
        elif question_type == "open-ended":
            prompt += "Provide a thoughtful response based on your role and experience. "
            prompt += "Keep your answer concise but authentic to your background."
        
        return prompt
    
    def _validate_response(self, response: str, question: Dict[str, Any]) -> str:
        """Validate and clean response based on question type"""
        question_type = question["type"]
        
        if question_type == "scale":
            # Extract number from response
            options = question.get("options", ["1", "2", "3", "4", "5"])
            for option in options:
                if option in response:
                    return option
            # If no valid option found, return middle value
            return options[len(options) // 2]
            
        elif question_type == "multiple choice":
            # Check if response matches any option
            options = question.get("options", [])
            response_lower = response.lower()
            
            for option in options:
                if option.lower() in response_lower or response_lower in option.lower():
                    return option
            
            # If no match, return the first option that appears in response
            for option in options:
                if any(word in response_lower for word in option.lower().split()):
                    return option
            
            # Default to first option if no match
            return options[0] if options else response
            
        elif question_type == "checkbox":
            # Parse comma-separated responses
            options = question.get("options", [])
            response_parts = [part.strip() for part in response.split(",")]
            
            matched_options = []
            for part in response_parts:
                part_lower = part.lower()
                for option in options:
                    if (option.lower() in part_lower or part_lower in option.lower()) and option not in matched_options:
                        matched_options.append(option)
            
            return ", ".join(matched_options) if matched_options else response
        
        # For open-ended questions, return as-is but limit length
        return response[:500] if len(response) > 500 else response
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            messages = [
                {"role": "user", "content": "Hello, this is a test. Please respond with 'OK'."}
            ]
            response = self._make_request_with_retry(messages, max_tokens=10)
            return "ok" in response.lower()
        except Exception as e:
            print(f"API connection test failed: {e}")
            return False