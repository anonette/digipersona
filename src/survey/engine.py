import time
from datetime import datetime
from typing import Dict, List, Any
from personas import Persona, PersonaDatabase
from ai import GPTClient
from .questions import SurveyQuestions

class SurveyEngine:
    """Main survey orchestration engine"""
    
    def __init__(self, questions_file: str, database_path: str):
        self.questions = SurveyQuestions(questions_file)
        self.database = PersonaDatabase(database_path)
        self.gpt_client = GPTClient()
        self.survey_id = f"ai_adoption_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def run_survey_for_persona(self, persona: Persona, progress_callback=None) -> Dict[str, Any]:
        """Run complete survey for a single persona"""
        print(f"Starting survey for persona {persona.id}: {persona.get_description()}")
        
        survey_responses = {}
        start_time = time.time()
        
        questions_list = self.questions.get_questions()
        total_questions = len(questions_list)
        
        for i, question in enumerate(questions_list, 1):
            try:
                if progress_callback:
                    progress_callback(persona.id, i, total_questions)
                
                print(f"  Question {question['question']}: {question['text'][:50]}...")
                
                # Get persona's response via GPT-4o
                response = self.gpt_client.get_persona_response(
                    persona.get_prompt_context(),
                    question
                )
                
                # Store response
                survey_responses[str(question["question"])] = {
                    "question": question["text"],
                    "response": response,
                    "type": question["type"]
                }
                
                # Save to database
                self.database.save_survey_response(
                    persona.id,
                    self.survey_id,
                    question["question"],
                    question["text"],
                    response,
                    question["type"]
                )
                
                print(f"    Response: {response}")
                
            except Exception as e:
                print(f"    Error getting response: {e}")
                # Store error response
                survey_responses[str(question["question"])] = {
                    "question": question["text"],
                    "response": "ERROR: Could not generate response",
                    "type": question["type"],
                    "error": str(e)
                }
        
        # Update persona with survey responses
        persona.add_survey_response(self.survey_id, survey_responses)
        self.database.save_persona(persona)
        
        completion_time = time.time() - start_time
        
        result = {
            "persona_id": persona.id,
            "survey_id": self.survey_id,
            "responses": survey_responses,
            "completion_time_seconds": round(completion_time, 2),
            "total_questions": total_questions,
            "successful_responses": len([r for r in survey_responses.values() if "error" not in r])
        }
        
        print(f"Completed survey for {persona.id} in {completion_time:.1f} seconds")
        return result
    
    def run_survey_for_all_personas(self, personas: List[Persona], progress_callback=None) -> List[Dict[str, Any]]:
        """Run survey for all personas"""
        print(f"Starting survey for {len(personas)} personas...")
        print(f"Survey ID: {self.survey_id}")
        
        results = []
        total_personas = len(personas)
        
        for i, persona in enumerate(personas, 1):
            try:
                print(f"\n[{i}/{total_personas}] Processing persona {persona.id}")
                
                result = self.run_survey_for_persona(
                    persona, 
                    lambda pid, q_num, q_total: progress_callback(i, total_personas, pid, q_num, q_total) if progress_callback else None
                )
                results.append(result)
                
            except Exception as e:
                print(f"Failed to complete survey for persona {persona.id}: {e}")
                results.append({
                    "persona_id": persona.id,
                    "survey_id": self.survey_id,
                    "error": str(e),
                    "completion_time_seconds": 0,
                    "total_questions": self.questions.get_question_count(),
                    "successful_responses": 0
                })
        
        return results
    
    def get_survey_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate survey completion statistics"""
        total_personas = len(results)
        successful_surveys = len([r for r in results if "error" not in r])
        failed_surveys = total_personas - successful_surveys
        
        total_questions = sum(r.get("total_questions", 0) for r in results)
        successful_responses = sum(r.get("successful_responses", 0) for r in results)
        
        total_time = sum(r.get("completion_time_seconds", 0) for r in results)
        avg_time_per_persona = total_time / total_personas if total_personas > 0 else 0
        
        return {
            "survey_id": self.survey_id,
            "total_personas": total_personas,
            "successful_surveys": successful_surveys,
            "failed_surveys": failed_surveys,
            "success_rate": (successful_surveys / total_personas * 100) if total_personas > 0 else 0,
            "total_questions_asked": total_questions,
            "successful_responses": successful_responses,
            "response_rate": (successful_responses / total_questions * 100) if total_questions > 0 else 0,
            "total_time_seconds": round(total_time, 2),
            "average_time_per_persona": round(avg_time_per_persona, 2),
            "questions_per_survey": self.questions.get_question_count()
        }
    
    def test_single_persona(self, persona: Persona, question_limit: int = 3) -> Dict[str, Any]:
        """Test survey with a single persona and limited questions"""
        print(f"Testing survey with persona {persona.id} (first {question_limit} questions)")
        
        questions_list = self.questions.get_questions()[:question_limit]
        survey_responses = {}
        start_time = time.time()
        
        for question in questions_list:
            try:
                print(f"Question {question['question']}: {question['text']}")
                
                response = self.gpt_client.get_persona_response(
                    persona.get_prompt_context(),
                    question
                )
                
                survey_responses[str(question["question"])] = {
                    "question": question["text"],
                    "response": response,
                    "type": question["type"]
                }
                
                print(f"Response: {response}\n")
                
            except Exception as e:
                print(f"Error: {e}\n")
                survey_responses[str(question["question"])] = {
                    "question": question["text"],
                    "response": f"ERROR: {e}",
                    "type": question["type"]
                }
        
        completion_time = time.time() - start_time
        
        return {
            "persona_id": persona.id,
            "test_responses": survey_responses,
            "completion_time_seconds": round(completion_time, 2),
            "questions_tested": len(questions_list)
        }