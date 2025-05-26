import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from .persona import Persona

class PersonaDatabase:
    """SQLite database manager for personas"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create personas table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personas (
                    id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    department TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    age_range TEXT NOT NULL,
                    experience TEXT NOT NULL,
                    location TEXT NOT NULL,
                    team_size TEXT NOT NULL,
                    response_history TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create survey responses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS survey_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id TEXT NOT NULL,
                    survey_id TEXT NOT NULL,
                    question_number INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    response TEXT NOT NULL,
                    response_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (id)
                )
            ''')
            
            conn.commit()
    
    def save_persona(self, persona: Persona):
        """Save or update persona in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO personas 
                (id, role, department, gender, age_range, experience, location, 
                 team_size, response_history, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                persona.id,
                persona.role,
                persona.department,
                persona.gender,
                persona.age_range,
                persona.experience,
                persona.location,
                persona.team_size,
                json.dumps(persona.response_history),
                persona.created_at.isoformat(),
                persona.last_updated.isoformat()
            ))
            
            conn.commit()
    
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Retrieve persona by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM personas WHERE id = ?', (persona_id,))
            row = cursor.fetchone()
            
            if row:
                return Persona(
                    id=row[0],
                    role=row[1],
                    department=row[2],
                    gender=row[3],
                    age_range=row[4],
                    experience=row[5],
                    location=row[6],
                    team_size=row[7],
                    response_history=json.loads(row[8] or '[]'),
                    created_at=datetime.fromisoformat(row[9]),
                    last_updated=datetime.fromisoformat(row[10])
                )
            return None
    
    def get_all_personas(self) -> List[Persona]:
        """Retrieve all personas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM personas ORDER BY created_at')
            rows = cursor.fetchall()
            
            personas = []
            for row in rows:
                personas.append(Persona(
                    id=row[0],
                    role=row[1],
                    department=row[2],
                    gender=row[3],
                    age_range=row[4],
                    experience=row[5],
                    location=row[6],
                    team_size=row[7],
                    response_history=json.loads(row[8] or '[]'),
                    created_at=datetime.fromisoformat(row[9]),
                    last_updated=datetime.fromisoformat(row[10])
                ))
            
            return personas
    
    def save_survey_response(self, persona_id: str, survey_id: str, 
                           question_number: int, question_text: str, 
                           response: str, response_type: str):
        """Save individual survey response"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO survey_responses 
                (persona_id, survey_id, question_number, question_text, response, response_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (persona_id, survey_id, question_number, question_text, response, response_type))
            
            conn.commit()
    
    def get_survey_responses(self, persona_id: str, survey_id: str) -> List[dict]:
        """Get survey responses for a persona"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT question_number, question_text, response, response_type, timestamp
                FROM survey_responses 
                WHERE persona_id = ? AND survey_id = ?
                ORDER BY question_number
            ''', (persona_id, survey_id))
            
            rows = cursor.fetchall()
            return [
                {
                    "question_number": row[0],
                    "question_text": row[1],
                    "response": row[2],
                    "response_type": row[3],
                    "timestamp": row[4]
                }
                for row in rows
            ]
    
    def count_personas(self) -> int:
        """Count total personas in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM personas')
            return cursor.fetchone()[0]