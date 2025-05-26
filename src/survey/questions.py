import json
from typing import List, Dict, Any

class SurveyQuestions:
    """Load and manage survey questions"""
    
    def __init__(self, questions_file: str):
        self.questions_file = questions_file
        self.questions = self._load_questions()
    
    def _load_questions(self) -> List[Dict[str, Any]]:
        """Load questions from JSON file"""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            # Validate question structure
            for question in questions:
                self._validate_question(question)
            
            return questions
        except FileNotFoundError:
            raise FileNotFoundError(f"Survey questions file not found: {self.questions_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in questions file: {e}")
    
    def _validate_question(self, question: Dict[str, Any]):
        """Validate question structure"""
        required_fields = ["question", "text", "type"]
        
        for field in required_fields:
            if field not in question:
                raise ValueError(f"Question missing required field: {field}")
        
        # Validate question types
        valid_types = ["scale", "multiple choice", "checkbox", "open-ended"]
        if question["type"] not in valid_types:
            raise ValueError(f"Invalid question type: {question['type']}")
        
        # Validate options for choice questions
        if question["type"] in ["scale", "multiple choice", "checkbox"]:
            if "options" not in question or not question["options"]:
                raise ValueError(f"Question type '{question['type']}' requires options")
    
    def get_questions(self) -> List[Dict[str, Any]]:
        """Get all questions"""
        return self.questions.copy()
    
    def get_question_by_number(self, question_number: int) -> Dict[str, Any]:
        """Get specific question by number"""
        for question in self.questions:
            if question["question"] == question_number:
                return question
        raise ValueError(f"Question {question_number} not found")
    
    def get_question_count(self) -> int:
        """Get total number of questions"""
        return len(self.questions)
    
    def get_questions_by_type(self, question_type: str) -> List[Dict[str, Any]]:
        """Get questions of specific type"""
        return [q for q in self.questions if q["type"] == question_type]
    
    def get_survey_summary(self) -> Dict[str, Any]:
        """Get summary of survey structure"""
        summary = {
            "total_questions": len(self.questions),
            "question_types": {},
            "question_numbers": [q["question"] for q in self.questions]
        }
        
        for question in self.questions:
            q_type = question["type"]
            summary["question_types"][q_type] = summary["question_types"].get(q_type, 0) + 1
        
        return summary
    
    def validate_response(self, question_number: int, response: str) -> bool:
        """Validate if response is appropriate for question type"""
        try:
            question = self.get_question_by_number(question_number)
            question_type = question["type"]
            
            if question_type == "scale":
                options = question.get("options", [])
                return response in options
            
            elif question_type == "multiple choice":
                options = question.get("options", [])
                return response in options
            
            elif question_type == "checkbox":
                options = question.get("options", [])
                response_parts = [part.strip() for part in response.split(",")]
                return all(part in options for part in response_parts)
            
            elif question_type == "open-ended":
                return len(response.strip()) > 0
            
            return False
            
        except ValueError:
            return False