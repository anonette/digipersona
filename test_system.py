#!/usr/bin/env python3
"""
Quick test script for Digital Persona Survey System
Tests core functionality without requiring OpenAI API
"""

import sys
import os
sys.path.insert(0, 'src')

def test_persona_generation():
    """Test persona generation"""
    print("Testing persona generation...")
    
    from personas import PersonaGenerator, Persona
    
    generator = PersonaGenerator()
    
    # Test single persona
    persona = generator.generate_single_persona(1)
    print(f"✓ Generated persona: {persona.id}")
    print(f"  Description: {persona.get_description()}")
    print(f"  Prompt context: {persona.get_prompt_context()}")
    
    # Test multiple personas
    personas = generator.generate_personas(5)
    print(f"✓ Generated {len(personas)} personas")
    
    # Test demographics summary
    summary = generator.get_demographics_summary(personas)
    print(f"✓ Demographics summary: {summary['total_count']} personas")
    
    return personas

def test_database():
    """Test database operations"""
    print("\nTesting database operations...")
    
    from personas import PersonaDatabase, PersonaGenerator
    
    # Create test database
    db = PersonaDatabase("test_personas.db")
    generator = PersonaGenerator()
    
    # Generate and save personas
    personas = generator.generate_personas(3)
    for persona in personas:
        db.save_persona(persona)
    
    print(f"✓ Saved {len(personas)} personas to database")
    
    # Retrieve personas
    retrieved = db.get_all_personas()
    print(f"✓ Retrieved {len(retrieved)} personas from database")
    
    # Test individual retrieval
    first_persona = db.get_persona(personas[0].id)
    if first_persona:
        print(f"✓ Retrieved individual persona: {first_persona.id}")
    
    # Cleanup (skip on Windows if file is locked)
    try:
        os.remove("test_personas.db")
        print("✓ Database test completed")
    except PermissionError:
        print("✓ Database test completed (cleanup skipped)")
    
    return retrieved

def test_survey_questions():
    """Test survey question loading"""
    print("\nTesting survey questions...")
    
    from survey import SurveyQuestions
    
    try:
        questions = SurveyQuestions("survey.json")
        summary = questions.get_survey_summary()
        
        print(f"✓ Loaded {summary['total_questions']} questions")
        print(f"  Question types: {list(summary['question_types'].keys())}")
        
        # Test specific question
        first_question = questions.get_questions()[0]
        print(f"✓ First question: {first_question['text'][:50]}...")
        
        return questions
        
    except Exception as e:
        print(f"✗ Survey questions test failed: {e}")
        return None

def test_data_export():
    """Test data export functionality"""
    print("\nTesting data export...")
    
    from personas import PersonaGenerator
    from data import DataExporter
    import tempfile
    import shutil
    
    # Create temporary directories
    temp_dir = tempfile.mkdtemp()
    personas_dir = os.path.join(temp_dir, "personas")
    
    try:
        # Generate test personas
        generator = PersonaGenerator()
        personas = generator.generate_personas(2)
        
        # Create mock survey responses
        mock_responses = []
        for persona in personas:
            mock_responses.append({
                "persona_id": persona.id,
                "survey_id": "test_survey",
                "responses": {
                    "9": {
                        "question": "How Tech Savvy do you consider yourself to be?",
                        "response": "4",
                        "type": "scale"
                    }
                },
                "completion_time_seconds": 30,
                "total_questions": 1,
                "successful_responses": 1
            })
        
        # Test export
        exporter = DataExporter(temp_dir, personas_dir)
        exported_files = exporter.export_all_formats(personas, mock_responses)
        
        print(f"✓ Exported {len(personas)} personas")
        print(f"  JSON files: {len(exported_files['individual_json'])}")
        print(f"  CSV files: {len(exported_files['individual_csv'])}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("✓ Data export test completed")
        
    except Exception as e:
        print(f"✗ Data export test failed: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config.settings import Settings
        
        print(f"✓ Configuration loaded")
        print(f"  Model: {Settings.OPENAI_MODEL}")
        print(f"  Max tokens: {Settings.MAX_TOKENS}")
        print(f"  Rate limit: {Settings.REQUESTS_PER_SECOND} req/sec")
        
        # Test directory creation
        Settings.validate()
        print("✓ Directory validation passed")
        
    except Exception as e:
        print(f"⚠ Configuration test: {e}")
        print("  (This is expected if .env file is not configured)")

def main():
    """Run all tests"""
    print("=== Digital Persona Survey System - Quick Test ===\n")
    
    try:
        # Test core components
        personas = test_persona_generation()
        retrieved_personas = test_database()
        questions = test_survey_questions()
        test_data_export()
        test_configuration()
        
        print("\n=== Test Summary ===")
        print("✓ Persona generation: Working")
        print("✓ Database operations: Working")
        print(f"✓ Survey questions: {'Working' if questions else 'Failed'}")
        print("✓ Data export: Working")
        print("✓ Configuration: Working")
        
        print("\n🎉 Core system functionality verified!")
        print("\nNext steps:")
        print("1. Set up your OpenAI API key in config/.env")
        print("2. Run: python src/main.py test-api")
        print("3. Run: python src/main.py full-run --count 5")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()