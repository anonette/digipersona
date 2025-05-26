import random
from typing import List
from .persona import Persona

class PersonaGenerator:
    """Generate diverse personas based on demographic templates"""
    
    # Demographic templates
    ROLES = [
        "Product Manager", "Software Engineer", "Data Scientist", "Marketing Manager",
        "Sales Director", "Operations Manager", "HR Manager", "Finance Manager",
        "UX Designer", "DevOps Engineer", "Business Analyst", "Project Manager",
        "Tech Lead", "Engineering Manager", "VP of Engineering", "CTO"
    ]
    
    DEPARTMENTS = [
        "Product", "Engineering", "Marketing", "Sales", "Operations", 
        "Human Resources", "Finance", "Design", "Data Science", "IT"
    ]
    
    GENDERS = ["Male", "Female", "Non-binary"]
    
    AGE_RANGES = ["25-34", "35-44", "45-54", "55-64"]
    
    EXPERIENCE_LEVELS = [
        "2-5 years", "5-10 years", "Over 10 years", "Over 15 years"
    ]
    
    LOCATIONS = [
        "USA", "Canada", "UK", "Germany", "France", "Netherlands", 
        "Sweden", "Australia", "Japan", "Singapore", "India", "Brazil"
    ]
    
    TEAM_SIZES = [
        "0-5 employees", "5-10 employees", "10-20 employees", "Over 20 employees"
    ]
    
    # Role-Department mappings for realistic combinations
    ROLE_DEPARTMENT_MAP = {
        "Product Manager": ["Product"],
        "Software Engineer": ["Engineering"],
        "Data Scientist": ["Data Science", "Engineering"],
        "Marketing Manager": ["Marketing"],
        "Sales Director": ["Sales"],
        "Operations Manager": ["Operations"],
        "HR Manager": ["Human Resources"],
        "Finance Manager": ["Finance"],
        "UX Designer": ["Design", "Product"],
        "DevOps Engineer": ["Engineering", "IT"],
        "Business Analyst": ["Product", "Operations"],
        "Project Manager": ["Product", "Engineering", "Operations"],
        "Tech Lead": ["Engineering"],
        "Engineering Manager": ["Engineering"],
        "VP of Engineering": ["Engineering"],
        "CTO": ["Engineering"]
    }
    
    # Experience-based team size probabilities
    EXPERIENCE_TEAM_SIZE_MAP = {
        "2-5 years": ["0-5 employees", "5-10 employees"],
        "5-10 years": ["0-5 employees", "5-10 employees", "10-20 employees"],
        "Over 10 years": ["5-10 employees", "10-20 employees", "Over 20 employees"],
        "Over 15 years": ["10-20 employees", "Over 20 employees"]
    }
    
    def __init__(self):
        self.generated_ids = set()
    
    def generate_persona_id(self, role: str, index: int) -> str:
        """Generate unique persona ID"""
        role_abbrev = ''.join([word[0] for word in role.split()]).upper()
        persona_id = f"{role_abbrev}_{index:03d}"
        
        # Ensure uniqueness
        counter = 1
        original_id = persona_id
        while persona_id in self.generated_ids:
            persona_id = f"{original_id}_{counter}"
            counter += 1
        
        self.generated_ids.add(persona_id)
        return persona_id
    
    def generate_single_persona(self, index: int) -> Persona:
        """Generate a single realistic persona"""
        role = random.choice(self.ROLES)
        department = random.choice(self.ROLE_DEPARTMENT_MAP.get(role, self.DEPARTMENTS))
        gender = random.choice(self.GENDERS)
        age_range = random.choice(self.AGE_RANGES)
        experience = random.choice(self.EXPERIENCE_LEVELS)
        location = random.choice(self.LOCATIONS)
        
        # Choose team size based on experience level
        possible_team_sizes = self.EXPERIENCE_TEAM_SIZE_MAP.get(
            experience, self.TEAM_SIZES
        )
        team_size = random.choice(possible_team_sizes)
        
        persona_id = self.generate_persona_id(role, index)
        
        return Persona(
            id=persona_id,
            role=role,
            department=department,
            gender=gender,
            age_range=age_range,
            experience=experience,
            location=location,
            team_size=team_size
        )
    
    def generate_personas(self, count: int) -> List[Persona]:
        """Generate multiple diverse personas"""
        personas = []
        
        for i in range(1, count + 1):
            persona = self.generate_single_persona(i)
            personas.append(persona)
        
        return personas
    
    def generate_balanced_personas(self, count: int) -> List[Persona]:
        """Generate personas with balanced demographics"""
        personas = []
        
        # Calculate distribution
        roles_per_type = max(1, count // len(self.ROLES))
        
        index = 1
        for role in self.ROLES:
            for _ in range(roles_per_type):
                if len(personas) >= count:
                    break
                
                department = random.choice(self.ROLE_DEPARTMENT_MAP.get(role, self.DEPARTMENTS))
                gender = random.choice(self.GENDERS)
                age_range = random.choice(self.AGE_RANGES)
                experience = random.choice(self.EXPERIENCE_LEVELS)
                location = random.choice(self.LOCATIONS)
                
                possible_team_sizes = self.EXPERIENCE_TEAM_SIZE_MAP.get(
                    experience, self.TEAM_SIZES
                )
                team_size = random.choice(possible_team_sizes)
                
                persona_id = self.generate_persona_id(role, index)
                
                personas.append(Persona(
                    id=persona_id,
                    role=role,
                    department=department,
                    gender=gender,
                    age_range=age_range,
                    experience=experience,
                    location=location,
                    team_size=team_size
                ))
                
                index += 1
        
        # Fill remaining slots with random personas
        while len(personas) < count:
            persona = self.generate_single_persona(index)
            personas.append(persona)
            index += 1
        
        return personas[:count]
    
    def get_demographics_summary(self, personas: List[Persona]) -> dict:
        """Get summary statistics of generated personas"""
        summary = {
            "total_count": len(personas),
            "roles": {},
            "departments": {},
            "genders": {},
            "age_ranges": {},
            "experience_levels": {},
            "locations": {},
            "team_sizes": {}
        }
        
        for persona in personas:
            # Count occurrences
            summary["roles"][persona.role] = summary["roles"].get(persona.role, 0) + 1
            summary["departments"][persona.department] = summary["departments"].get(persona.department, 0) + 1
            summary["genders"][persona.gender] = summary["genders"].get(persona.gender, 0) + 1
            summary["age_ranges"][persona.age_range] = summary["age_ranges"].get(persona.age_range, 0) + 1
            summary["experience_levels"][persona.experience] = summary["experience_levels"].get(persona.experience, 0) + 1
            summary["locations"][persona.location] = summary["locations"].get(persona.location, 0) + 1
            summary["team_sizes"][persona.team_size] = summary["team_sizes"].get(persona.team_size, 0) + 1
        
        return summary