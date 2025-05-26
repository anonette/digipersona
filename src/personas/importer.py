import csv
import json
from typing import List, Dict, Any, Optional
from .persona import Persona
from .database import PersonaDatabase

class PersonaImporter:
    """Import personas from CSV files or manual input"""
    
    def __init__(self, database_path: str):
        self.database = PersonaDatabase(database_path)
    
    def import_from_csv(self, csv_file_path: str) -> List[Persona]:
        """Import personas from CSV file"""
        personas = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        persona = self._create_persona_from_row(row, row_num)
                        personas.append(persona)
                        
                        # Save to database
                        self.database.save_persona(persona)
                        
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}")
                        continue
            
            print(f"✓ Successfully imported {len(personas)} personas from {csv_file_path}")
            return personas
            
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
    
    def _create_persona_from_row(self, row: Dict[str, str], row_num: int) -> Persona:
        """Create persona from CSV row"""
        
        # Required fields mapping
        field_mapping = {
            'id': ['id', 'persona_id', 'ID'],
            'role': ['role', 'job_title', 'position', 'title'],
            'department': ['department', 'dept', 'team'],
            'gender': ['gender', 'sex'],
            'age_range': ['age_range', 'age', 'age_group'],
            'experience': ['experience', 'years_experience', 'exp'],
            'location': ['location', 'country', 'region'],
            'team_size': ['team_size', 'manages', 'team', 'employees']
        }
        
        # Extract values using flexible field names
        persona_data = {}
        for field, possible_names in field_mapping.items():
            value = None
            for name in possible_names:
                if name in row and row[name].strip():
                    value = row[name].strip()
                    break
            
            if not value:
                if field == 'id':
                    # Generate ID if not provided
                    value = f"IMPORT_{row_num:03d}"
                else:
                    raise ValueError(f"Required field '{field}' not found or empty in row {row_num}")
            
            persona_data[field] = value
        
        # Validate and normalize values
        persona_data = self._validate_persona_data(persona_data, row_num)
        
        return Persona(
            id=persona_data['id'],
            role=persona_data['role'],
            department=persona_data['department'],
            gender=persona_data['gender'],
            age_range=persona_data['age_range'],
            experience=persona_data['experience'],
            location=persona_data['location'],
            team_size=persona_data['team_size']
        )
    
    def _validate_persona_data(self, data: Dict[str, str], row_num: int) -> Dict[str, str]:
        """Validate and normalize persona data"""
        
        # Valid options for each field
        valid_options = {
            'gender': ['Male', 'Female', 'Non-binary', 'M', 'F', 'NB'],
            'age_range': ['25-34', '35-44', '45-54', '55-64'],
            'experience': ['2-5 years', '5-10 years', 'Over 10 years', 'Over 15 years'],
            'team_size': ['0-5 employees', '5-10 employees', '10-20 employees', 'Over 20 employees']
        }
        
        # Normalize gender
        gender_map = {'M': 'Male', 'F': 'Female', 'NB': 'Non-binary'}
        if data['gender'] in gender_map:
            data['gender'] = gender_map[data['gender']]
        
        # Validate fields with predefined options
        for field, options in valid_options.items():
            if field in data and data[field] not in options:
                # Try to find close match
                value_lower = data[field].lower()
                for option in options:
                    if value_lower in option.lower() or option.lower() in value_lower:
                        data[field] = option
                        break
                else:
                    print(f"Warning: Invalid {field} '{data[field]}' in row {row_num}, using first valid option")
                    data[field] = options[0]
        
        return data
    
    def create_persona_manually(self, persona_data: Dict[str, str]) -> Persona:
        """Create a single persona from manual input"""
        
        # Validate required fields
        required_fields = ['id', 'role', 'department', 'gender', 'age_range', 'experience', 'location', 'team_size']
        for field in required_fields:
            if field not in persona_data or not persona_data[field]:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Validate data
        validated_data = self._validate_persona_data(persona_data, 0)
        
        # Create persona
        persona = Persona(
            id=validated_data['id'],
            role=validated_data['role'],
            department=validated_data['department'],
            gender=validated_data['gender'],
            age_range=validated_data['age_range'],
            experience=validated_data['experience'],
            location=validated_data['location'],
            team_size=validated_data['team_size']
        )
        
        # Save to database
        self.database.save_persona(persona)
        
        print(f"✓ Created persona: {persona.id} - {persona.get_description()}")
        return persona
    
    def create_csv_template(self, output_file: str = "persona_template.csv"):
        """Create a CSV template for importing personas"""
        
        headers = [
            'id', 'role', 'department', 'gender', 'age_range', 
            'experience', 'location', 'team_size'
        ]
        
        sample_data = [
            {
                'id': 'PM_CUSTOM_001',
                'role': 'Product Manager',
                'department': 'Product',
                'gender': 'Female',
                'age_range': '35-44',
                'experience': 'Over 10 years',
                'location': 'USA',
                'team_size': '10-20 employees'
            },
            {
                'id': 'SE_CUSTOM_002',
                'role': 'Software Engineer',
                'department': 'Engineering',
                'gender': 'Male',
                'age_range': '25-34',
                'experience': '5-10 years',
                'location': 'Germany',
                'team_size': '0-5 employees'
            },
            {
                'id': 'MM_CUSTOM_003',
                'role': 'Marketing Manager',
                'department': 'Marketing',
                'gender': 'Non-binary',
                'age_range': '45-54',
                'experience': 'Over 15 years',
                'location': 'Canada',
                'team_size': 'Over 20 employees'
            }
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"✓ Created CSV template: {output_file}")
        print("Valid options for each field:")
        print("  gender: Male, Female, Non-binary")
        print("  age_range: 25-34, 35-44, 45-54, 55-64")
        print("  experience: 2-5 years, 5-10 years, Over 10 years, Over 15 years")
        print("  team_size: 0-5 employees, 5-10 employees, 10-20 employees, Over 20 employees")
        
        return output_file
    
    def import_from_json(self, json_file_path: str) -> List[Persona]:
        """Import personas from JSON file"""
        personas = []
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # Array of personas
                persona_list = data
            elif isinstance(data, dict):
                if 'personas' in data:
                    # Object with personas array
                    persona_list = data['personas']
                else:
                    # Single persona object
                    persona_list = [data]
            else:
                raise ValueError("Invalid JSON structure")
            
            for i, persona_data in enumerate(persona_list, 1):
                try:
                    # Extract demographics if nested
                    if 'demographics' in persona_data:
                        demo_data = persona_data['demographics']
                        demo_data['id'] = persona_data.get('persona_id', f"JSON_{i:03d}")
                    else:
                        demo_data = persona_data
                    
                    persona = self.create_persona_manually(demo_data)
                    personas.append(persona)
                    
                except Exception as e:
                    print(f"Error processing persona {i}: {e}")
                    continue
            
            print(f"✓ Successfully imported {len(personas)} personas from {json_file_path}")
            return personas
            
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON file: {e}")
        except Exception as e:
            raise Exception(f"Error reading JSON file: {e}")
    
    def get_import_summary(self) -> Dict[str, Any]:
        """Get summary of all personas in database"""
        all_personas = self.database.get_all_personas()
        
        summary = {
            "total_personas": len(all_personas),
            "import_sources": {},
            "demographics": {
                "roles": {},
                "departments": {},
                "locations": {},
                "age_ranges": {},
                "experience_levels": {}
            }
        }
        
        for persona in all_personas:
            # Identify import source
            if persona.id.startswith("IMPORT_"):
                source = "CSV Import"
            elif persona.id.startswith("JSON_"):
                source = "JSON Import"
            elif "CUSTOM" in persona.id:
                source = "Manual Creation"
            else:
                source = "Generated"
            
            summary["import_sources"][source] = summary["import_sources"].get(source, 0) + 1
            
            # Count demographics
            summary["demographics"]["roles"][persona.role] = summary["demographics"]["roles"].get(persona.role, 0) + 1
            summary["demographics"]["departments"][persona.department] = summary["demographics"]["departments"].get(persona.department, 0) + 1
            summary["demographics"]["locations"][persona.location] = summary["demographics"]["locations"].get(persona.location, 0) + 1
            summary["demographics"]["age_ranges"][persona.age_range] = summary["demographics"]["age_ranges"].get(persona.age_range, 0) + 1
            summary["demographics"]["experience_levels"][persona.experience] = summary["demographics"]["experience_levels"].get(persona.experience, 0) + 1
        
        return summary