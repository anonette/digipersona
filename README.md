# Digital Persona Survey System

A comprehensive Python system that creates and manages digital personas with demographic characteristics, connects them to GPT-4o, and conducts AI adoption surveys while maintaining persona consistency for future interviews.

## 🌟 Features

- **🎭 Persona Management**: Generate 100+ diverse digital personas with realistic demographic profiles
- **🤖 AI Integration**: Connect personas to GPT-4o for authentic survey responses
- **📊 Survey Engine**: Conduct structured surveys with multiple question types
- **🌐 Web Interface**: Modern Streamlit web app with real-time updates
- **💻 CLI Interface**: Command-line tools for automation and scripting
- **📈 Data Export**: Export results in JSON and CSV formats for analysis
- **🔄 Consistency**: Maintain persona characteristics across interactions
- **⚡ Scalability**: Handle large numbers of personas efficiently

## 🚀 Quick Start

### 1. Installation & Setup

```bash
# Clone or download the project
cd digipersona

# Automated setup (recommended)
python setup.py

# This will:
# - Create virtual environment
# - Install all dependencies
# - Create necessary directories
# - Set up configuration files
```

### 2. Configuration

```bash
# Edit the configuration file and add your OpenAI API key
# config/.env
OPENAI_API_KEY=your_api_key_here
```

### 3. Launch the System

#### Option A: Web Interface (Recommended)
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Launch Streamlit web interface
python run_streamlit.py

# Opens automatically at http://localhost:8501
```

#### Option B: Command Line Interface
```bash
# Activate virtual environment
venv\Scripts\activate

# Full pipeline: generate personas, run survey, export data
python src/main.py full-run --count 20

# Or run step by step:
python src/main.py generate --count 20 --balanced
python src/main.py survey
python src/main.py export
```

## 🌐 Streamlit Web Interface

The system includes a comprehensive web interface with:

### 🏠 Dashboard
- **System Overview**: Real-time metrics for personas, surveys, and exports
- **Quick Actions**: One-click generation, survey execution, and data export
- **Recent Activity**: Timeline of recent persona creation and survey completion

### 👥 Persona Management
- **View Personas**: Searchable table with filtering by role, location, department
- **Generate Personas**: Interactive form for balanced or random generation
- **Import Data**: Drag-and-drop CSV/JSON upload with preview
- **Manual Creation**: Step-by-step persona creation form
- **Download Templates**: Pre-built CSV templates for easy data entry

### 📊 Survey Management
- **Survey Questions**: Visual overview of all 18 questions with type distribution
- **Run Surveys**: Test mode (3 questions) or full survey execution
- **Real-time Progress**: Live progress tracking with persona-by-persona updates
- **Cost Estimation**: Automatic API cost calculation before survey execution

### 📈 Analytics & Results
- **Demographics Visualization**: Interactive charts showing role, location, and department distribution
- **Export Interface**: One-click export to multiple formats (JSON, CSV, individual files)
- **Survey Status**: Completion tracking and progress visualization

### ⚙️ Settings & Configuration
- **API Configuration**: Secure API key input with connection testing
- **System Information**: Current settings and file paths overview

## 📋 Usage Examples

### Generate Personas
```bash
# Web Interface: Use "Persona Management" → "Generate" tab
# CLI:
python src/main.py generate --count 50 --balanced
python src/main.py generate --count 100
```

### Import Custom Personas
```bash
# Web Interface: Use "Persona Management" → "Import" tab
# CLI:
python src/main.py create-template  # Download CSV template
python src/main.py import-csv --file my_personas.csv
python src/main.py import-json --file my_personas.json
python src/main.py create-persona  # Interactive creation
```

### Run Surveys
```bash
# Web Interface: Use "Survey Management" → "Run Survey" tab
# CLI:
python src/main.py test-survey  # Test with 3 questions
python src/main.py survey       # Full survey
python src/main.py survey --limit 10  # Limit to 10 personas
```

### Export Data
```bash
# Web Interface: Use "Analytics & Results" → "Export Data" tab
# CLI:
python src/main.py export
python src/main.py export --limit 25
```

### Check Status
```bash
# Web Interface: Dashboard shows real-time status
# CLI:
python src/main.py status
```

## 📁 Project Structure

```
digipersona/
├── streamlit_app.py          # Web interface
├── run_streamlit.py          # Web app launcher
├── setup.py                  # Automated setup script
├── src/
│   ├── personas/             # Persona management
│   │   ├── persona.py        # Persona data model
│   │   ├── generator.py      # Persona generation
│   │   ├── database.py       # SQLite operations
│   │   └── importer.py       # CSV/JSON import
│   ├── survey/               # Survey engine
│   │   ├── questions.py      # Question management
│   │   └── engine.py         # Survey orchestration
│   ├── ai/                   # GPT-4o integration
│   │   └── gpt_client.py     # OpenAI API client
│   ├── data/                 # Data export
│   │   └── exporter.py       # Multi-format export
│   └── main.py               # CLI interface
├── config/                   # Configuration
│   ├── settings.py           # System settings
│   ├── .env                  # API keys (create from .env.example)
│   └── .env.example          # Environment template
├── data/                     # Database storage
├── output/                   # Export files
│   └── personas/             # Individual persona files
├── survey.json               # Survey questions
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## 📊 Custom Persona Import

### CSV Import Format
The system accepts CSV files with the following columns:
- **id**: Unique identifier (e.g., PM_CUSTOM_001)
- **role**: Job title (e.g., Product Manager, Software Engineer)
- **department**: Department (e.g., Product, Engineering, Marketing)
- **gender**: Male, Female, or Non-binary
- **age_range**: 25-34, 35-44, 45-54, or 55-64
- **experience**: 2-5 years, 5-10 years, Over 10 years, or Over 15 years
- **location**: Country/region (e.g., USA, Germany, Canada)
- **team_size**: 0-5, 5-10, 10-20, or Over 20 employees

### JSON Import Format
```json
[
  {
    "id": "PM_CUSTOM_001",
    "role": "Product Manager",
    "department": "Product",
    "gender": "Female",
    "age_range": "35-44",
    "experience": "Over 10 years",
    "location": "USA",
    "team_size": "10-20 employees"
  }
]
```

### Manual Persona Creation
Use the web interface "Create Manual" tab or CLI:
```bash
python src/main.py create-persona
```

## 👥 Persona Demographics

The system generates diverse personas with:

- **Roles**: Product Manager, Software Engineer, Data Scientist, Marketing Manager, etc.
- **Departments**: Product, Engineering, Marketing, Sales, Operations, etc.
- **Demographics**: Various genders, age ranges (25-64), experience levels
- **Locations**: USA, Canada, UK, Germany, France, Netherlands, Sweden, Australia, etc.
- **Team Sizes**: 0-5, 5-10, 10-20, 20+ employees

## 📋 Survey Questions

The system uses 18 AI adoption questions covering:

- Tech-savviness and AI familiarity
- Generative AI tool usage
- AI adoption timeline and drivers
- Use cases and limitations
- Concerns and sentiment
- Organizational adaptation
- Societal impact and governance

## 📤 Output Formats

### Individual Persona Files
- **JSON**: Complete persona profile with survey responses
- **CSV**: Flattened data for individual analysis

### Master Files
- **JSON**: All personas in structured format
- **CSV**: Analysis-ready dataset with all responses

### Example Output Structure
```json
{
  "persona_id": "PM_001",
  "demographics": {
    "role": "Product Manager",
    "department": "Product",
    "gender": "Male",
    "age_range": "45-54",
    "experience": "Over 10 years",
    "location": "USA",
    "team_size": "Over 20 employees"
  },
  "survey_responses": {
    "9": {
      "question": "How Tech Savvy do you consider yourself to be?",
      "response": "4",
      "type": "scale"
    }
  }
}
```

## ⚙️ Configuration Options

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o
MAX_TOKENS=500
TEMPERATURE=0.7
```

### Settings (config/settings.py)
- Rate limiting: 3 requests/second
- Retry logic: 3 attempts with exponential backoff
- Database: SQLite for persona storage
- Output directories: Configurable paths

## 🎯 Persona Consistency

Personas maintain consistency through:

- **Demographic-based responses**: Answers reflect role, age, experience, location
- **Response history**: Previous interactions inform future responses
- **Authentic prompting**: Simple, demographic-focused prompts without artificial personality traits

### Example Persona Prompts
```
You are a global tech corporate manager who works in Product department, 
Male, age range: 45-54, has Over 10 years of experience, lives in USA, 
manages Over 20 employees.

Respond to survey questions authentically based on your role, experience, age, and location.
```

## 💰 API Usage and Costs

- **Model**: GPT-4o
- **Rate Limiting**: 3 requests per second
- **Token Usage**: ~500 tokens per response
- **Estimated Cost**: ~$0.02-0.05 per persona (18 questions)

For 100 personas: ~$2-5 total cost

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**
   ```bash
   # Web Interface: Use Settings → API Configuration
   # CLI: Edit config/.env
   OPENAI_API_KEY=your_actual_key_here
   ```

2. **Installation Issues**
   ```bash
   # Run automated setup
   python setup.py
   
   # Or manual installation
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Rate Limiting**
   ```bash
   # System automatically handles rate limits
   # Adjust REQUESTS_PER_SECOND in settings.py if needed
   ```

4. **Database Issues**
   ```bash
   # Delete and regenerate database
   rm data/personas.db
   python src/main.py generate --count 10
   ```

5. **Import Errors**
   ```bash
   # Use web interface for better error messages
   # Or check CSV/JSON format requirements above
   ```

## 🛠️ Development

### Adding New Question Types
1. Update `src/ai/gpt_client.py` - add prompt logic
2. Update `src/survey/questions.py` - add validation
3. Test with `python src/main.py test-survey`

### Extending Persona Demographics
1. Edit `src/personas/generator.py`
2. Add new demographic categories
3. Update role-department mappings

### Custom Export Formats
1. Extend `src/data/exporter.py`
2. Add new export methods
3. Update main.py export command

## 🎉 Key Features

### Web Interface Benefits
- **User-Friendly**: No command-line knowledge required
- **Real-time Feedback**: Live progress tracking and status updates
- **Interactive Visualizations**: Charts and graphs for data analysis
- **Error Handling**: Clear error messages with recovery suggestions
- **File Management**: Drag-and-drop uploads with automatic validation

### CLI Interface Benefits
- **Automation**: Perfect for scripts and batch processing
- **Integration**: Easy to integrate with other tools and workflows
- **Performance**: Direct access to all system components
- **Flexibility**: Full control over all parameters and options

### Data Management
- **Multiple Sources**: Generate, import CSV/JSON, or create manually
- **Persistent Storage**: SQLite database for reliable data management
- **Export Flexibility**: Multiple formats for different analysis needs
- **Future-Proof**: Designed for follow-up interviews and extended surveys

## 📄 License

This project is provided as-is for research and development purposes.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Use the web interface for better error messages
3. Test with a small number of personas first
4. Ensure OpenAI API key is valid and has sufficient credits
5. Check that all dependencies are installed correctly

---

**Ready to get started?** Run `python setup.py` and then `python run_streamlit.py` to launch the web interface!