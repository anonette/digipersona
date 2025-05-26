#!/usr/bin/env python3
"""
Digital Persona Import Demo
Demonstrates all import functionality
"""

import sys
import os
sys.path.insert(0, 'src')

def demo_csv_import():
    """Demonstrate CSV import functionality"""
    print("=== CSV Import Demo ===")
    
    from personas.importer import PersonaImporter
    
    # Create importer
    importer = PersonaImporter("demo_import.db")
    
    # Create a sample CSV
    sample_csv = "demo_personas.csv"
    with open(sample_csv, 'w', encoding='utf-8') as f:
        f.write("id,role,department,gender,age_range,experience,location,team_size\n")
        f.write("CEO_001,Chief Executive Officer,Executive,Female,45-54,Over 15 years,Sweden,Over 20 employees\n")
        f.write("CTO_002,Chief Technology Officer,Engineering,Male,35-44,Over 10 years,Finland,Over 20 employees\n")
        f.write("PM_003,Product Manager,Product,Non-binary,25-34,5-10 years,Norway,10-20 employees\n")
    
    print(f"Created sample CSV: {sample_csv}")
    
    # Import personas
    personas = importer.import_from_csv(sample_csv)
    
    print(f"Imported personas:")
    for persona in personas:
        print(f"  {persona.id}: {persona.get_description()}")
        print(f"    Prompt: {persona.get_prompt_context()}")
    
    # Show summary
    summary = importer.get_import_summary()
    print(f"\nImport Summary:")
    print(f"  Total personas: {summary['total_personas']}")
    print(f"  Sources: {summary['import_sources']}")
    
    # Cleanup
    os.remove(sample_csv)
    os.remove("demo_import.db")

def demo_manual_creation():
    """Demonstrate manual persona creation"""
    print("\n=== Manual Creation Demo ===")
    
    from personas.importer import PersonaImporter
    
    # Create importer
    importer = PersonaImporter("demo_manual.db")
    
    # Create personas manually
    personas_data = [
        {
            'id': 'MANUAL_001',
            'role': 'AI Research Scientist',
            'department': 'Research',
            'gender': 'Female',
            'age_range': '25-34',
            'experience': '5-10 years',
            'location': 'Japan',
            'team_size': '5-10 employees'
        },
        {
            'id': 'MANUAL_002',
            'role': 'Blockchain Developer',
            'department': 'Engineering',
            'gender': 'Male',
            'age_range': '35-44',
            'experience': 'Over 10 years',
            'location': 'Singapore',
            'team_size': '0-5 employees'
        }
    ]
    
    created_personas = []
    for data in personas_data:
        persona = importer.create_persona_manually(data)
        created_personas.append(persona)
    
    print(f"\nCreated {len(created_personas)} personas manually")
    
    # Cleanup
    os.remove("demo_manual.db")

def demo_template_creation():
    """Demonstrate template creation"""
    print("\n=== Template Creation Demo ===")
    
    from personas.importer import PersonaImporter
    
    # Create importer
    importer = PersonaImporter("demo_template.db")
    
    # Create template
    template_file = importer.create_csv_template("demo_template.csv")
    
    print(f"Template created: {template_file}")
    
    # Show template content
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"\nTemplate content:")
        print(content)
    
    # Cleanup
    os.remove(template_file)
    os.remove("demo_template.db")

def demo_json_import():
    """Demonstrate JSON import functionality"""
    print("\n=== JSON Import Demo ===")
    
    from personas.importer import PersonaImporter
    import json
    
    # Create importer
    importer = PersonaImporter("demo_json.db")
    
    # Create sample JSON
    sample_data = [
        {
            "id": "JSON_001",
            "role": "DevOps Engineer",
            "department": "IT",
            "gender": "Non-binary",
            "age_range": "25-34",
            "experience": "2-5 years",
            "location": "Australia",
            "team_size": "5-10 employees"
        },
        {
            "id": "JSON_002",
            "role": "Security Analyst",
            "department": "IT",
            "gender": "Female",
            "age_range": "35-44",
            "experience": "Over 10 years",
            "location": "Brazil",
            "team_size": "10-20 employees"
        }
    ]
    
    sample_json = "demo_personas.json"
    with open(sample_json, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Created sample JSON: {sample_json}")
    
    # Import personas
    personas = importer.import_from_json(sample_json)
    
    print(f"Imported {len(personas)} personas from JSON")
    for persona in personas:
        print(f"  {persona.id}: {persona.role} in {persona.location}")
    
    # Cleanup
    os.remove(sample_json)
    os.remove("demo_json.db")

def main():
    """Run all import demos"""
    print("🎭 Digital Persona Import System - Demo")
    print("=" * 50)
    
    try:
        demo_csv_import()
        demo_manual_creation()
        demo_template_creation()
        demo_json_import()
        
        print("\n" + "=" * 50)
        print("✅ All import demos completed successfully!")
        print("\nAvailable import commands:")
        print("1. python src/main.py create-template")
        print("2. python src/main.py import-csv --file your_file.csv")
        print("3. python src/main.py import-json --file your_file.json")
        print("4. python src/main.py create-persona")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()