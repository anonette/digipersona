import os
import shutil
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from personas import PersonaDatabase
from data import DataExporter
from config.settings import Settings

class ResearchArchiver:
    """Archive research data and clear database for new research"""
    
    def __init__(self):
        self.database = PersonaDatabase(Settings.DATABASE_PATH)
        self.exporter = DataExporter(Settings.OUTPUT_DIR, Settings.PERSONAS_DIR)
        self.archive_base_dir = "archives"
        
        # Ensure archive directory exists
        os.makedirs(self.archive_base_dir, exist_ok=True)
    
    def create_archive(self, research_name: str, description: str = "") -> Dict[str, str]:
        """Create a complete archive of current research"""
        
        # Generate archive directory name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{research_name}_{timestamp}"
        archive_dir = os.path.join(self.archive_base_dir, archive_name)
        
        print(f"Creating research archive: {archive_name}")
        
        # Create archive directory structure
        os.makedirs(archive_dir, exist_ok=True)
        os.makedirs(os.path.join(archive_dir, "database"), exist_ok=True)
        os.makedirs(os.path.join(archive_dir, "exports"), exist_ok=True)
        os.makedirs(os.path.join(archive_dir, "metadata"), exist_ok=True)
        
        # Get all personas for export
        personas = self.database.get_all_personas()
        
        if not personas:
            raise ValueError("No research data found to archive")
        
        # Create comprehensive export
        print("Exporting all research data...")
        
        # Get survey results for each persona
        survey_results = []
        for persona in personas:
            if persona.response_history:
                latest_survey = persona.response_history[-1]
                survey_results.append({
                    "persona_id": persona.id,
                    "survey_id": latest_survey["survey_id"],
                    "responses": latest_survey["responses"],
                    "completion_time_seconds": 0,
                    "total_questions": len(latest_survey["responses"]),
                    "successful_responses": len(latest_survey["responses"])
                })
        
        # Export all formats to archive
        archive_exporter = DataExporter(
            os.path.join(archive_dir, "exports"),
            os.path.join(archive_dir, "exports", "personas")
        )
        
        exported_files = archive_exporter.export_all_formats(personas, survey_results)
        
        # Copy database file
        if os.path.exists(Settings.DATABASE_PATH):
            shutil.copy2(Settings.DATABASE_PATH, os.path.join(archive_dir, "database", "personas.db"))
        
        # Create research metadata
        metadata = {
            "research_name": research_name,
            "description": description,
            "archive_created": datetime.now().isoformat(),
            "archive_name": archive_name,
            "statistics": {
                "total_personas": len(personas),
                "personas_with_surveys": len([p for p in personas if p.response_history]),
                "total_survey_responses": sum(len(p.response_history) for p in personas),
                "exported_files": {
                    "individual_json": len(exported_files["individual_json"]),
                    "individual_csv": len(exported_files["individual_csv"]),
                    "master_json": len(exported_files["master_json"]),
                    "analysis_csv": len(exported_files["analysis_csv"])
                }
            },
            "personas_summary": self._get_personas_summary(personas),
            "survey_summary": self._get_survey_summary(personas)
        }
        
        # Save metadata
        with open(os.path.join(archive_dir, "metadata", "research_info.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create README for the archive
        self._create_archive_readme(archive_dir, metadata)
        
        print(f"✅ Research archived successfully!")
        print(f"Archive location: {archive_dir}")
        print(f"Total personas archived: {len(personas)}")
        print(f"Surveys archived: {len(survey_results)}")
        
        return {
            "archive_name": archive_name,
            "archive_path": archive_dir,
            "personas_count": len(personas),
            "surveys_count": len(survey_results),
            "created_at": datetime.now().isoformat()
        }
    
    def clear_current_research(self, confirm: bool = False) -> Dict[str, str]:
        """Clear current research data (database and output files)"""
        
        if not confirm:
            raise ValueError("Must confirm clearing research data. Set confirm=True")
        
        print("Clearing current research data...")
        
        # Count current data
        personas = self.database.get_all_personas()
        personas_count = len(personas)
        
        # Clear database
        if os.path.exists(Settings.DATABASE_PATH):
            os.remove(Settings.DATABASE_PATH)
            print(f"✅ Database cleared ({personas_count} personas removed)")
        
        # Clear output directory
        if os.path.exists(Settings.OUTPUT_DIR):
            shutil.rmtree(Settings.OUTPUT_DIR)
            os.makedirs(Settings.OUTPUT_DIR, exist_ok=True)
            os.makedirs(Settings.PERSONAS_DIR, exist_ok=True)
            print("✅ Output directory cleared")
        
        # Reinitialize database
        self.database = PersonaDatabase(Settings.DATABASE_PATH)
        print("✅ Fresh database initialized")
        
        return {
            "cleared_personas": personas_count,
            "cleared_at": datetime.now().isoformat(),
            "status": "Research data cleared successfully"
        }
    
    def archive_and_clear(self, research_name: str, description: str = "") -> Dict[str, str]:
        """Archive current research and clear for new research"""
        
        print("=== Archive and Clear Research ===")
        
        # First create archive
        archive_info = self.create_archive(research_name, description)
        
        # Then clear current data
        clear_info = self.clear_current_research(confirm=True)
        
        result = {
            "archive_name": archive_info["archive_name"],
            "archive_path": archive_info["archive_path"],
            "archived_personas": archive_info["personas_count"],
            "archived_surveys": archive_info["surveys_count"],
            "cleared_personas": clear_info["cleared_personas"],
            "completed_at": datetime.now().isoformat(),
            "status": "Research archived and cleared successfully"
        }
        
        print(f"🎉 Research '{research_name}' archived and system cleared for new research!")
        
        return result
    
    def list_archives(self) -> List[Dict[str, str]]:
        """List all available research archives"""
        
        archives = []
        
        if not os.path.exists(self.archive_base_dir):
            return archives
        
        for archive_dir in os.listdir(self.archive_base_dir):
            archive_path = os.path.join(self.archive_base_dir, archive_dir)
            metadata_file = os.path.join(archive_path, "metadata", "research_info.json")
            
            if os.path.isdir(archive_path) and os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    archives.append({
                        "archive_name": metadata["archive_name"],
                        "research_name": metadata["research_name"],
                        "description": metadata.get("description", ""),
                        "created_at": metadata["archive_created"],
                        "personas_count": metadata["statistics"]["total_personas"],
                        "surveys_count": metadata["statistics"]["personas_with_surveys"],
                        "archive_path": archive_path
                    })
                except Exception as e:
                    print(f"Warning: Could not read archive metadata for {archive_dir}: {e}")
        
        # Sort by creation date (newest first)
        archives.sort(key=lambda x: x["created_at"], reverse=True)
        
        return archives
    
    def restore_archive(self, archive_name: str) -> Dict[str, str]:
        """Restore research from archive (WARNING: Overwrites current data)"""
        
        archive_path = os.path.join(self.archive_base_dir, archive_name)
        
        if not os.path.exists(archive_path):
            raise ValueError(f"Archive not found: {archive_name}")
        
        print(f"Restoring research from archive: {archive_name}")
        print("⚠️  WARNING: This will overwrite current research data!")
        
        # Clear current data first
        self.clear_current_research(confirm=True)
        
        # Restore database
        archive_db = os.path.join(archive_path, "database", "personas.db")
        if os.path.exists(archive_db):
            shutil.copy2(archive_db, Settings.DATABASE_PATH)
            print("✅ Database restored")
        
        # Restore output files
        archive_exports = os.path.join(archive_path, "exports")
        if os.path.exists(archive_exports):
            if os.path.exists(Settings.OUTPUT_DIR):
                shutil.rmtree(Settings.OUTPUT_DIR)
            shutil.copytree(archive_exports, Settings.OUTPUT_DIR)
            print("✅ Export files restored")
        
        # Reinitialize database connection
        self.database = PersonaDatabase(Settings.DATABASE_PATH)
        
        # Get restored data info
        personas = self.database.get_all_personas()
        
        print(f"🎉 Research restored successfully!")
        print(f"Restored {len(personas)} personas")
        
        return {
            "archive_name": archive_name,
            "restored_personas": len(personas),
            "restored_at": datetime.now().isoformat(),
            "status": "Research restored successfully"
        }
    
    def _get_personas_summary(self, personas: List) -> Dict[str, Dict[str, int]]:
        """Get summary statistics of personas"""
        summary = {
            "roles": {},
            "departments": {},
            "locations": {},
            "age_ranges": {},
            "experience_levels": {}
        }
        
        for persona in personas:
            summary["roles"][persona.role] = summary["roles"].get(persona.role, 0) + 1
            summary["departments"][persona.department] = summary["departments"].get(persona.department, 0) + 1
            summary["locations"][persona.location] = summary["locations"].get(persona.location, 0) + 1
            summary["age_ranges"][persona.age_range] = summary["age_ranges"].get(persona.age_range, 0) + 1
            summary["experience_levels"][persona.experience] = summary["experience_levels"].get(persona.experience, 0) + 1
        
        return summary
    
    def _get_survey_summary(self, personas: List) -> Dict[str, int]:
        """Get summary of survey completion"""
        total_surveys = sum(len(p.response_history) for p in personas)
        personas_with_surveys = len([p for p in personas if p.response_history])
        
        return {
            "total_surveys_completed": total_surveys,
            "personas_with_surveys": personas_with_surveys,
            "personas_without_surveys": len(personas) - personas_with_surveys
        }
    
    def _create_archive_readme(self, archive_dir: str, metadata: Dict):
        """Create README file for the archive"""
        readme_content = f"""# Research Archive: {metadata['research_name']}

## Archive Information
- **Research Name**: {metadata['research_name']}
- **Description**: {metadata.get('description', 'No description provided')}
- **Archive Created**: {metadata['archive_created']}
- **Archive Name**: {metadata['archive_name']}

## Research Statistics
- **Total Personas**: {metadata['statistics']['total_personas']}
- **Personas with Surveys**: {metadata['statistics']['personas_with_surveys']}
- **Total Survey Responses**: {metadata['statistics']['total_survey_responses']}

## Exported Files
- **Individual JSON files**: {metadata['statistics']['exported_files']['individual_json']}
- **Individual CSV files**: {metadata['statistics']['exported_files']['individual_csv']}
- **Master JSON files**: {metadata['statistics']['exported_files']['master_json']}
- **Analysis CSV files**: {metadata['statistics']['exported_files']['analysis_csv']}

## Archive Contents
- `database/` - SQLite database backup
- `exports/` - All exported data files
  - `personas/` - Individual persona files (JSON & CSV)
  - Master analysis files
- `metadata/` - Research metadata and statistics

## Demographics Summary
### Roles
{self._format_dict_for_readme(metadata['personas_summary']['roles'])}

### Departments  
{self._format_dict_for_readme(metadata['personas_summary']['departments'])}

### Locations
{self._format_dict_for_readme(metadata['personas_summary']['locations'])}

## Survey Summary
- **Total Surveys Completed**: {metadata['survey_summary']['total_surveys_completed']}
- **Personas with Surveys**: {metadata['survey_summary']['personas_with_surveys']}
- **Personas without Surveys**: {metadata['survey_summary']['personas_without_surveys']}

## Restoration
To restore this research:
```bash
python src/main.py restore-archive --name {metadata['archive_name']}
```

**WARNING**: Restoration will overwrite current research data.
"""
        
        with open(os.path.join(archive_dir, "README.md"), 'w') as f:
            f.write(readme_content)
    
    def _format_dict_for_readme(self, data_dict: Dict[str, int]) -> str:
        """Format dictionary for README display"""
        if not data_dict:
            return "- None"
        
        lines = []
        for key, value in sorted(data_dict.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{key}**: {value}")
        
        return "\n".join(lines)