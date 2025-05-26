#!/usr/bin/env python3
"""
Digital Persona Survey System
Main application entry point
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from personas import PersonaGenerator, PersonaDatabase, PersonaImporter
from survey import SurveyEngine
from data import DataExporter
from ai import GPTClient
from research import ResearchArchiver

def setup_environment():
    """Setup and validate environment"""
    try:
        Settings.validate()
        print("✓ Environment setup complete")
        return True
    except Exception as e:
        print(f"✗ Environment setup failed: {e}")
        print("\nPlease ensure:")
        print("1. Copy config/.env.example to config/.env")
        print("2. Add your OpenAI API key to config/.env")
        print("3. Install requirements: pip install -r requirements.txt")
        return False

def test_api_connection():
    """Test OpenAI API connection"""
    print("Testing OpenAI API connection...")
    try:
        client = GPTClient()
        if client.test_connection():
            print("✓ OpenAI API connection successful")
            return True
        else:
            print("✗ OpenAI API connection failed")
            return False
    except Exception as e:
        print(f"✗ OpenAI API connection error: {e}")
        return False

def generate_personas(count: int, balanced: bool = True):
    """Generate personas and save to database"""
    print(f"\nGenerating {count} personas...")
    
    generator = PersonaGenerator()
    database = PersonaDatabase(Settings.DATABASE_PATH)
    
    if balanced:
        personas = generator.generate_balanced_personas(count)
    else:
        personas = generator.generate_personas(count)
    
    # Save to database
    for persona in personas:
        database.save_persona(persona)
    
    # Show summary
    summary = generator.get_demographics_summary(personas)
    print(f"✓ Generated {len(personas)} personas")
    print(f"  Roles: {len(summary['roles'])} different roles")
    print(f"  Locations: {len(summary['locations'])} different locations")
    print(f"  Departments: {len(summary['departments'])} different departments")
    
    return personas

def import_personas_from_csv(csv_file: str):
    """Import personas from CSV file"""
    print(f"\nImporting personas from CSV: {csv_file}")
    
    importer = PersonaImporter(Settings.DATABASE_PATH)
    
    try:
        personas = importer.import_from_csv(csv_file)
        
        # Show summary
        summary = importer.get_import_summary()
        print(f"✓ Import completed")
        print(f"  Total personas in database: {summary['total_personas']}")
        print(f"  Import sources: {summary['import_sources']}")
        
        return personas
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return None

def import_personas_from_json(json_file: str):
    """Import personas from JSON file"""
    print(f"\nImporting personas from JSON: {json_file}")
    
    importer = PersonaImporter(Settings.DATABASE_PATH)
    
    try:
        personas = importer.import_from_json(json_file)
        
        # Show summary
        summary = importer.get_import_summary()
        print(f"✓ Import completed")
        print(f"  Total personas in database: {summary['total_personas']}")
        print(f"  Import sources: {summary['import_sources']}")
        
        return personas
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return None

def create_persona_template(template_type: str = "csv"):
    """Create template files for persona import"""
    print(f"\nCreating {template_type.upper()} template...")
    
    importer = PersonaImporter(Settings.DATABASE_PATH)
    
    if template_type.lower() == "csv":
        template_file = importer.create_csv_template()
        print(f"✓ CSV template created: {template_file}")
    else:
        print("✗ Only CSV templates are currently supported")

def create_manual_persona():
    """Interactive persona creation"""
    print("\n=== Manual Persona Creation ===")
    print("Enter persona details (press Enter for each field):")
    
    persona_data = {}
    
    # Required fields with prompts
    fields = {
        'id': 'Persona ID (e.g., PM_CUSTOM_001): ',
        'role': 'Role/Job Title (e.g., Product Manager): ',
        'department': 'Department (e.g., Product, Engineering, Marketing): ',
        'gender': 'Gender (Male/Female/Non-binary): ',
        'age_range': 'Age Range (25-34, 35-44, 45-54, 55-64): ',
        'experience': 'Experience (2-5 years, 5-10 years, Over 10 years, Over 15 years): ',
        'location': 'Location/Country (e.g., USA, Germany, Canada): ',
        'team_size': 'Team Size (0-5, 5-10, 10-20, Over 20 employees): '
    }
    
    for field, prompt in fields.items():
        while True:
            value = input(prompt).strip()
            if value:
                persona_data[field] = value
                break
            else:
                print("This field is required. Please enter a value.")
    
    # Create persona
    try:
        importer = PersonaImporter(Settings.DATABASE_PATH)
        persona = importer.create_persona_manually(persona_data)
        
        print(f"\n✓ Persona created successfully!")
        print(f"  ID: {persona.id}")
        print(f"  Description: {persona.get_description()}")
        
        return persona
        
    except Exception as e:
        print(f"✗ Failed to create persona: {e}")
        return None

def run_survey(personas_limit: int = None, test_mode: bool = False):
    """Run survey for all personas"""
    print(f"\n{'Testing survey' if test_mode else 'Running survey'}...")
    
    # Load personas from database
    database = PersonaDatabase(Settings.DATABASE_PATH)
    personas = database.get_all_personas()
    
    if not personas:
        print("✗ No personas found in database. Generate personas first.")
        return None
    
    if personas_limit:
        personas = personas[:personas_limit]
        print(f"Limited to first {len(personas)} personas")
    
    # Initialize survey engine
    engine = SurveyEngine(Settings.SURVEY_FILE, Settings.DATABASE_PATH)
    
    if test_mode:
        # Test with first persona only
        test_persona = personas[0]
        result = engine.test_single_persona(test_persona, question_limit=3)
        print(f"✓ Test completed for {test_persona.id}")
        return [result]
def archive_research(research_name: str, description: str = ""):
    """Archive current research data"""
    print(f"\nArchiving research: {research_name}")
    
    try:
        archiver = ResearchArchiver()
        result = archiver.create_archive(research_name, description)
        
        print(f"✅ Research archived successfully!")
        print(f"Archive name: {result['archive_name']}")
        print(f"Archive path: {result['archive_path']}")
        print(f"Personas archived: {result['personas_count']}")
        print(f"Surveys archived: {result['surveys_count']}")
        
        return result
        
    except Exception as e:
        print(f"✗ Archive failed: {e}")
        return None

def clear_research(confirm: bool = False):
    """Clear current research data"""
    if not confirm:
        print("⚠️  This will permanently delete all current research data!")
        print("Use --confirm flag to proceed: python src/main.py clear-research --confirm")
        return None
    
    print("\nClearing current research data...")
    
    try:
        archiver = ResearchArchiver()
        result = archiver.clear_current_research(confirm=True)
        
        print(f"✅ Research data cleared!")
        print(f"Personas removed: {result['cleared_personas']}")
        print("Database and output files cleared")
        print("Ready for new research!")
        
        return result
        
    except Exception as e:
        print(f"✗ Clear failed: {e}")
        return None

def archive_and_clear_research(research_name: str, description: str = ""):
    """Archive current research and clear for new research"""
    print(f"\nArchiving and clearing research: {research_name}")
    
    try:
        archiver = ResearchArchiver()
        result = archiver.archive_and_clear(research_name, description)
        
        print(f"🎉 Research archived and cleared!")
        print(f"Archive: {result['archive_name']}")
        print(f"Archived: {result['archived_personas']} personas, {result['archived_surveys']} surveys")
        print(f"Cleared: {result['cleared_personas']} personas")
        print("System ready for new research!")
        
        return result
        
    except Exception as e:
        print(f"✗ Archive and clear failed: {e}")
        return None

def list_research_archives():
    """List all available research archives"""
    print("\nAvailable Research Archives:")
    
    try:
        archiver = ResearchArchiver()
        archives = archiver.list_archives()
        
        if not archives:
            print("No archives found.")
            return []
        
        print(f"Found {len(archives)} archives:\n")
        
        for i, archive in enumerate(archives, 1):
            print(f"{i}. {archive['research_name']}")
            print(f"   Archive: {archive['archive_name']}")
            print(f"   Created: {archive['created_at']}")
            print(f"   Personas: {archive['personas_count']}, Surveys: {archive['surveys_count']}")
            if archive['description']:
                print(f"   Description: {archive['description']}")
            print(f"   Path: {archive['archive_path']}")
            print()
        
        return archives
        
    except Exception as e:
        print(f"✗ List archives failed: {e}")
        return []

def restore_research_archive(archive_name: str, confirm: bool = False):
    """Restore research from archive"""
    if not confirm:
        print("⚠️  This will overwrite all current research data!")
        print("Use --confirm flag to proceed: python src/main.py restore-archive --name archive_name --confirm")
        return None
    
    print(f"\nRestoring research from archive: {archive_name}")
    
    try:
        archiver = ResearchArchiver()
        result = archiver.restore_archive(archive_name)
        
        print(f"🎉 Research restored successfully!")
        print(f"Archive: {result['archive_name']}")
        print(f"Restored: {result['restored_personas']} personas")
        print("Research data is now active!")
        
        return result
        
    except Exception as e:
        print(f"✗ Restore failed: {e}")
        return None
    else:
        # Run full survey
        def progress_callback(persona_idx, total_personas, persona_id, question_num, total_questions):
            print(f"  [{persona_idx}/{total_personas}] {persona_id}: Question {question_num}/{total_questions}")
        
        results = engine.run_survey_for_all_personas(personas, progress_callback)
        
        # Show statistics
        stats = engine.get_survey_statistics(results)
        print(f"\n✓ Survey completed!")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Total time: {stats['total_time_seconds']:.1f} seconds")
        print(f"  Average per persona: {stats['average_time_per_persona']:.1f} seconds")
        
        return results

def export_data(personas_limit: int = None):
    """Export all data in multiple formats"""
    print("\nExporting data...")
    
    # Load personas and survey results
    database = PersonaDatabase(Settings.DATABASE_PATH)
    personas = database.get_all_personas()
    
    if not personas:
        print("✗ No personas found in database")
        return
    
    if personas_limit:
        personas = personas[:personas_limit]
    
    # Get latest survey results for each persona
    survey_results = []
    for persona in personas:
        if persona.response_history:
            latest_survey = persona.response_history[-1]
            survey_results.append({
                "persona_id": persona.id,
                "survey_id": latest_survey["survey_id"],
                "responses": latest_survey["responses"],
                "completion_time_seconds": 0,  # Not tracked in history
                "total_questions": len(latest_survey["responses"]),
                "successful_responses": len(latest_survey["responses"])
            })
    
    # Export data
    exporter = DataExporter(Settings.OUTPUT_DIR, Settings.PERSONAS_DIR)
    exported_files = exporter.export_all_formats(personas, survey_results)
    
    print(f"✓ Exported {len(personas)} personas")
    print(f"  Individual JSON files: {len(exported_files['individual_json'])}")
    print(f"  Individual CSV files: {len(exported_files['individual_csv'])}")
    print(f"  Master JSON files: {len(exported_files['master_json'])}")
    print(f"  Analysis CSV files: {len(exported_files['analysis_csv'])}")

def show_status():
    """Show current system status"""
    print("\n=== Digital Persona Survey System Status ===")
    
    # Check database
    database = PersonaDatabase(Settings.DATABASE_PATH)
    persona_count = database.count_personas()
    print(f"Personas in database: {persona_count}")
    
    # Check survey file
    if os.path.exists(Settings.SURVEY_FILE):
        from survey import SurveyQuestions
        questions = SurveyQuestions(Settings.SURVEY_FILE)
        summary = questions.get_survey_summary()
        print(f"Survey questions loaded: {summary['total_questions']}")
        print(f"Question types: {', '.join(summary['question_types'].keys())}")
    else:
        print("Survey file: Not found")
    
    # Check output directory
    if os.path.exists(Settings.PERSONAS_DIR):
        persona_files = len([f for f in os.listdir(Settings.PERSONAS_DIR) if f.endswith('.json')])
        print(f"Exported persona files: {persona_files}")
    else:
        print("Output directory: Not created")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Digital Persona Survey System")
    parser.add_argument("command", choices=[
        "setup", "test-api", "generate", "survey", "test-survey", "export", "status", "full-run",
        "import-csv", "import-json", "create-template", "create-persona",
        "archive-research", "clear-research", "archive-and-clear", "list-archives", "restore-archive"
    ], help="Command to execute")
    
    parser.add_argument("--count", type=int, default=10, help="Number of personas to generate")
    parser.add_argument("--limit", type=int, help="Limit number of personas for survey/export")
    parser.add_argument("--balanced", action="store_true", help="Generate balanced demographics")
    parser.add_argument("--file", type=str, help="File path for import operations")
    parser.add_argument("--template", type=str, default="csv", help="Template type (csv)")
    parser.add_argument("--name", type=str, help="Research name for archive operations")
    parser.add_argument("--description", type=str, default="", help="Description for research archive")
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive operations")
    
    args = parser.parse_args()
    
    print("=== Digital Persona Survey System ===")
    print(f"Command: {args.command}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.command == "setup":
        setup_environment()
    
    elif args.command == "test-api":
        if setup_environment():
            test_api_connection()
    
    elif args.command == "generate":
        if setup_environment():
            generate_personas(args.count, args.balanced)
    
    elif args.command == "survey":
        if setup_environment() and test_api_connection():
            run_survey(args.limit)
    
    elif args.command == "test-survey":
        if setup_environment() and test_api_connection():
            run_survey(args.limit, test_mode=True)
    
    elif args.command == "export":
        export_data(args.limit)
    
    elif args.command == "import-csv":
        if not args.file:
            print("✗ Please specify CSV file with --file parameter")
        else:
            import_personas_from_csv(args.file)
    
    elif args.command == "import-json":
        if not args.file:
            print("✗ Please specify JSON file with --file parameter")
        else:
            import_personas_from_json(args.file)
    
    elif args.command == "create-template":
        create_persona_template(args.template)
    
    elif args.command == "create-persona":
        create_manual_persona()
    elif args.command == "archive-research":
        if not args.name:
            print("✗ Please specify research name with --name parameter")
        else:
            archive_research(args.name, args.description)
    
    elif args.command == "clear-research":
        clear_research(args.confirm)
    
    elif args.command == "archive-and-clear":
        if not args.name:
            print("✗ Please specify research name with --name parameter")
        else:
            archive_and_clear_research(args.name, args.description)
    
    elif args.command == "list-archives":
        list_research_archives()
    
    elif args.command == "restore-archive":
        if not args.name:
            print("✗ Please specify archive name with --name parameter")
        else:
            restore_research_archive(args.name, args.confirm)
    
    elif args.command == "status":
        show_status()
    
    elif args.command == "full-run":
        print("\n=== Full Pipeline Run ===")
        if not setup_environment():
            return
        if not test_api_connection():
            return
        
        # Generate personas
        personas = generate_personas(args.count, args.balanced)
        
        # Run survey
        results = run_survey(args.limit)
        if results:
            # Export data
            export_data(args.limit)
        
        print("\n✓ Full pipeline completed successfully!")

if __name__ == "__main__":
    main()