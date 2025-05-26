from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import json

@dataclass
class Persona:
    """Digital persona with demographic characteristics"""
    id: str
    role: str
    department: str
    gender: str
    age_range: str
    experience: str
    location: str
    team_size: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    response_history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert persona to dictionary"""
        return {
            "id": self.id,
            "role": self.role,
            "department": self.department,
            "gender": self.gender,
            "age_range": self.age_range,
            "experience": self.experience,
            "location": self.location,
            "team_size": self.team_size,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "response_history": self.response_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Persona':
        """Create persona from dictionary"""
        return cls(
            id=data["id"],
            role=data["role"],
            department=data["department"],
            gender=data["gender"],
            age_range=data["age_range"],
            experience=data["experience"],
            location=data["location"],
            team_size=data["team_size"],
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
            response_history=data.get("response_history", [])
        )
    
    def get_description(self) -> str:
        """Get natural language description of persona"""
        return (f"a {self.role.lower()} who works in {self.department} department, "
                f"{self.gender}, age range: {self.age_range}, "
                f"has {self.experience} of experience, lives in {self.location}, "
                f"manages {self.team_size} employees")
    
    def add_survey_response(self, survey_id: str, responses: Dict):
        """Add survey responses to history"""
        response_entry = {
            "survey_id": survey_id,
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        }
        self.response_history.append(response_entry)
        self.last_updated = datetime.now()
    
    def get_prompt_context(self) -> str:
        """Generate GPT prompt context for this persona"""
        return (f"You are {self.get_description()}. "
                f"Respond to survey questions authentically based on your role, "
                f"experience, age, and location.")