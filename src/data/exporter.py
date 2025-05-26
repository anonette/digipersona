import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any
from personas import Persona, PersonaDatabase

class DataExporter:
    """Export persona and survey data in multiple formats"""
    
    def __init__(self, output_dir: str, personas_dir: str):
        self.output_dir = output_dir
        self.personas_dir = personas_dir
        
        # Ensure directories exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(personas_dir, exist_ok=True)
    
    def export_persona_json(self, persona: Persona, survey_responses: Dict[str, Any] = None) -> str:
        """Export individual persona to JSON file"""
        
        # Build persona data structure
        persona_data = {
            "persona_id": persona.id,
            "demographics": {
                "role": persona.role,
                "department": persona.department,
                "gender": persona.gender,
                "age_range": persona.age_range,
                "experience": persona.experience,
                "location": persona.location,
                "team_size": persona.team_size
            },
            "metadata": {
                "created_at": persona.created_at.isoformat(),
                "last_updated": persona.last_updated.isoformat()
            }
        }
        
        # Add survey responses if provided
        if survey_responses:
            persona_data["survey_responses"] = survey_responses["responses"]
            persona_data["survey_metadata"] = {
                "survey_id": survey_responses["survey_id"],
                "completion_time_seconds": survey_responses["completion_time_seconds"],
                "total_questions": survey_responses["total_questions"],
                "successful_responses": survey_responses["successful_responses"]
            }
        elif persona.response_history:
            # Use latest survey from history
            latest_survey = persona.response_history[-1]
            persona_data["survey_responses"] = latest_survey["responses"]
            persona_data["survey_metadata"] = {
                "survey_id": latest_survey["survey_id"],
                "timestamp": latest_survey["timestamp"]
            }
        
        # Write to file
        filename = f"{persona.id.lower()}.json"
        filepath = os.path.join(self.personas_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(persona_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def export_persona_csv(self, persona: Persona, survey_responses: Dict[str, Any] = None) -> str:
        """Export individual persona to CSV file"""
        
        # Prepare CSV data
        csv_data = {
            "persona_id": persona.id,
            "role": persona.role,
            "department": persona.department,
            "gender": persona.gender,
            "age_range": persona.age_range,
            "experience": persona.experience,
            "location": persona.location,
            "team_size": persona.team_size,
            "created_at": persona.created_at.isoformat(),
            "last_updated": persona.last_updated.isoformat()
        }
        
        # Add survey responses
        responses_to_use = None
        if survey_responses:
            responses_to_use = survey_responses["responses"]
            csv_data["survey_id"] = survey_responses["survey_id"]
            csv_data["completion_time_seconds"] = survey_responses["completion_time_seconds"]
        elif persona.response_history:
            latest_survey = persona.response_history[-1]
            responses_to_use = latest_survey["responses"]
            csv_data["survey_id"] = latest_survey["survey_id"]
            csv_data["survey_timestamp"] = latest_survey["timestamp"]
        
        # Add individual question responses
        if responses_to_use:
            for question_num, response_data in responses_to_use.items():
                csv_data[f"q{question_num}_response"] = response_data["response"]
                csv_data[f"q{question_num}_type"] = response_data["type"]
        
        # Write to CSV file
        filename = f"{persona.id.lower()}.csv"
        filepath = os.path.join(self.personas_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data.keys())
                writer.writeheader()
                writer.writerow(csv_data)
        
        return filepath
    
    def export_all_personas_json(self, personas: List[Persona], survey_results: List[Dict[str, Any]] = None) -> str:
        """Export all personas to a single JSON file"""
        
        # Create results mapping for quick lookup
        results_map = {}
        if survey_results:
            results_map = {result["persona_id"]: result for result in survey_results}
        
        all_personas_data = {
            "export_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_personas": len(personas),
                "export_type": "complete_dataset"
            },
            "personas": []
        }
        
        for persona in personas:
            persona_data = {
                "persona_id": persona.id,
                "demographics": {
                    "role": persona.role,
                    "department": persona.department,
                    "gender": persona.gender,
                    "age_range": persona.age_range,
                    "experience": persona.experience,
                    "location": persona.location,
                    "team_size": persona.team_size
                },
                "metadata": {
                    "created_at": persona.created_at.isoformat(),
                    "last_updated": persona.last_updated.isoformat()
                }
            }
            
            # Add survey data if available
            if persona.id in results_map:
                result = results_map[persona.id]
                persona_data["survey_responses"] = result["responses"]
                persona_data["survey_metadata"] = {
                    "survey_id": result["survey_id"],
                    "completion_time_seconds": result["completion_time_seconds"],
                    "total_questions": result["total_questions"],
                    "successful_responses": result["successful_responses"]
                }
            elif persona.response_history:
                latest_survey = persona.response_history[-1]
                persona_data["survey_responses"] = latest_survey["responses"]
                persona_data["survey_metadata"] = {
                    "survey_id": latest_survey["survey_id"],
                    "timestamp": latest_survey["timestamp"]
                }
            
            all_personas_data["personas"].append(persona_data)
        
        # Write to file
        filename = f"all_personas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_personas_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def export_analysis_csv(self, personas: List[Persona], survey_results: List[Dict[str, Any]] = None) -> str:
        """Export flattened data for analysis"""
        
        # Create results mapping
        results_map = {}
        if survey_results:
            results_map = {result["persona_id"]: result for result in survey_results}
        
        # Collect all possible question numbers for headers
        all_questions = set()
        for persona in personas:
            if persona.id in results_map:
                all_questions.update(results_map[persona.id]["responses"].keys())
            elif persona.response_history:
                for survey in persona.response_history:
                    all_questions.update(survey["responses"].keys())
        
        all_questions = sorted(all_questions, key=lambda x: int(x))
        
        # Prepare CSV headers
        headers = [
            "persona_id", "role", "department", "gender", "age_range", 
            "experience", "location", "team_size", "created_at", "survey_id"
        ]
        
        # Add question headers
        for q_num in all_questions:
            headers.extend([f"q{q_num}_question", f"q{q_num}_response", f"q{q_num}_type"])
        
        # Prepare data rows
        csv_rows = []
        for persona in personas:
            row = {
                "persona_id": persona.id,
                "role": persona.role,
                "department": persona.department,
                "gender": persona.gender,
                "age_range": persona.age_range,
                "experience": persona.experience,
                "location": persona.location,
                "team_size": persona.team_size,
                "created_at": persona.created_at.isoformat(),
                "survey_id": ""
            }
            
            # Add survey responses
            responses_to_use = None
            if persona.id in results_map:
                result = results_map[persona.id]
                responses_to_use = result["responses"]
                row["survey_id"] = result["survey_id"]
            elif persona.response_history:
                latest_survey = persona.response_history[-1]
                responses_to_use = latest_survey["responses"]
                row["survey_id"] = latest_survey["survey_id"]
            
            # Fill in question responses
            if responses_to_use:
                for q_num in all_questions:
                    if q_num in responses_to_use:
                        response_data = responses_to_use[q_num]
                        row[f"q{q_num}_question"] = response_data["question"]
                        row[f"q{q_num}_response"] = response_data["response"]
                        row[f"q{q_num}_type"] = response_data["type"]
                    else:
                        row[f"q{q_num}_question"] = ""
                        row[f"q{q_num}_response"] = ""
                        row[f"q{q_num}_type"] = ""
            
            csv_rows.append(row)
        
        # Write CSV file
        filename = f"analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if csv_rows:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(csv_rows)
        
        return filepath
    
    def export_all_formats(self, personas: List[Persona], survey_results: List[Dict[str, Any]] = None) -> Dict[str, List[str]]:
        """Export all personas in all formats"""
        
        print("Exporting persona data in multiple formats...")
        
        exported_files = {
            "individual_json": [],
            "individual_csv": [],
            "master_json": [],
            "analysis_csv": []
        }
        
        # Create results mapping
        results_map = {}
        if survey_results:
            results_map = {result["persona_id"]: result for result in survey_results}
        
        # Export individual files
        for i, persona in enumerate(personas, 1):
            print(f"  Exporting persona {i}/{len(personas)}: {persona.id}")
            
            survey_data = results_map.get(persona.id)
            
            # Individual JSON
            json_file = self.export_persona_json(persona, survey_data)
            exported_files["individual_json"].append(json_file)
            
            # Individual CSV
            csv_file = self.export_persona_csv(persona, survey_data)
            exported_files["individual_csv"].append(csv_file)
        
        # Export master files
        print("  Exporting master JSON file...")
        master_json = self.export_all_personas_json(personas, survey_results)
        exported_files["master_json"].append(master_json)
        
        print("  Exporting analysis CSV file...")
        analysis_csv = self.export_analysis_csv(personas, survey_results)
        exported_files["analysis_csv"].append(analysis_csv)
        
        print(f"Export complete! Files saved to:")
        print(f"  Individual files: {self.personas_dir}")
        print(f"  Master files: {self.output_dir}")
        
        return exported_files