#!/usr/bin/env python3
"""
Digital Persona Survey System - Demo
Simple demonstration without API calls
"""

import sys
import os
import json

# Add src to Python path
sys.path.insert(0, 'src')

def demo_persona_generation():
    """Demonstrate persona generation"""
    print("=== Persona Generation Demo ===")
    
    from personas.generator import PersonaGenerator
    from personas.database import PersonaDatabase
    
    # Generate personas
    generator = PersonaGenerator()
    personas = generator.generate_balanced_personas(5)
    
    print(f"Generated {len(personas)} personas:")
    for persona in personas:
        print(f"  {persona.id}: {persona.get_description()}")
    
    # Save to database
    db = PersonaDatabase("demo_personas.db")
    for persona in personas:
        db.save_persona(persona)
    
    print(f"\nSaved to database: demo_personas.db")
    
    # Show demographics
    summary = generator.get_demographics_summary(personas)
    print(f"\nDemographics Summary:")
    print(f"  Roles: {list(summary['roles'].keys())}")
    print(f"  Locations: {list(summary['locations'].keys())}")
    
    return personas

def demo_survey_questions():
    """Demonstrate survey question loading"""
    print("\n=== Survey Questions Demo ===")
    
    from survey.questions import SurveyQuestions
    
    try:
        questions = SurveyQuestions("survey.json")
        summary = questions.get_survey_summary()
        
        print(f"Loaded {summary['total_questions']} survey questions")
        print(f"Question types: {list(summary['question_types'].keys())}")
        
        # Show first few questions
        print(f"\nFirst 3 questions:")
        for i, question in enumerate(questions.get_questions()[:3], 1):
            print(f"  {i}. {question['text']}")
            print(f"     Type: {question['type']}")
            if 'options' in question:
                print(f"     Options: {question['options']}")
        
        return questions
        
    except Exception as e:
        print(f"Error loading questions: {e}")
        return None

def demo_persona_prompts():
    """Demonstrate persona prompt generation"""
    print("\n=== Persona Prompts Demo ===")
    
    from personas.generator import PersonaGenerator
    
    generator = PersonaGenerator()
    personas = generator.generate_personas(3)
    
    print("Sample persona prompts for GPT-4o:")
    for i, persona in enumerate(personas, 1):
        print(f"\n{i}. Persona {persona.id}:")
        print(f"   Demographics: {persona.role}, {persona.age_range}, {persona.experience}")
        print(f"   Location: {persona.location}, Team: {persona.team_size}")
        print(f"   Prompt: {persona.get_prompt_context()}")

def demo_export_structure():
    """Demonstrate export data structure"""
    print("\n=== Export Structure Demo ===")
    
    from personas.generator import PersonaGenerator
    
    generator = PersonaGenerator()
    persona = generator.generate_single_persona(1)
    
    # Mock survey response
    mock_response = {
        "9": {
            "question": "How Tech Savvy do you consider yourself to be?",
            "response": "4",
            "type": "scale"
        },
        "10": {
            "question": "How familiar are you with generative AI technologies?",
            "response": "3",
            "type": "scale"
        }
    }
    
    # Show JSON structure
    export_data = {
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
        "survey_responses": mock_response
    }
    
    print("Sample JSON export structure:")
    print(json.dumps(export_data, indent=2))

def main():
    """Run demonstration"""
    print("🎭 Digital Persona Survey System - Demo")
    print("=" * 50)
    
    try:
        # Run demos
        personas = demo_persona_generation()
        questions = demo_survey_questions()
        demo_persona_prompts()
        demo_export_structure()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\nNext steps to run the full system:")
        print("1. Set up OpenAI API key in config/.env")
        print("2. Install requirements: pip install -r requirements.txt")
        print("3. Run: python src/main.py full-run --count 10")
        
        # Cleanup
        if os.path.exists("demo_personas.db"):
            os.remove("demo_personas.db")
            
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()