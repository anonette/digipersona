import streamlit as st
import pandas as pd
import json
import os
import sys
import io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
sys.path.insert(0, 'src')

from personas import PersonaGenerator, PersonaDatabase, PersonaImporter, Persona
from survey import SurveyEngine, SurveyQuestions
from data import DataExporter
from ai import GPTClient
from config.settings import Settings

# Page configuration
st.set_page_config(
    page_title="Digital Persona Survey System",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'database' not in st.session_state:
    st.session_state.database = PersonaDatabase(Settings.DATABASE_PATH)
if 'personas_generated' not in st.session_state:
    st.session_state.personas_generated = False
if 'survey_completed' not in st.session_state:
    st.session_state.survey_completed = False

def main():
    """Main Streamlit application"""
    
    # Sidebar navigation
    st.sidebar.title("🎭 Digital Persona Survey System")
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        [
            "🏠 Dashboard",
            "👥 Persona Management", 
            "📊 Survey Management",
            "📈 Analytics & Results",
            "⚙️ Settings & Configuration"
        ]
    )
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👥 Persona Management":
        show_persona_management()
    elif page == "📊 Survey Management":
        show_survey_management()
    elif page == "📈 Analytics & Results":
        show_analytics()
    elif page == "⚙️ Settings & Configuration":
        show_settings()

def show_dashboard():
    """Dashboard overview page"""
    st.title("🏠 Dashboard")
    st.markdown("Welcome to the Digital Persona Survey System")
    
    # System status cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        persona_count = st.session_state.database.count_personas()
        st.metric("Total Personas", persona_count)
    
    with col2:
        try:
            questions = SurveyQuestions(Settings.SURVEY_FILE)
            question_count = questions.get_question_count()
            st.metric("Survey Questions", question_count)
        except:
            st.metric("Survey Questions", "Error")
    
    with col3:
        # Count personas with survey responses
        personas = st.session_state.database.get_all_personas()
        completed_surveys = len([p for p in personas if p.response_history])
        st.metric("Completed Surveys", completed_surveys)
    
    with col4:
        # Check if output directory exists and count files
        if os.path.exists(Settings.PERSONAS_DIR):
            export_count = len([f for f in os.listdir(Settings.PERSONAS_DIR) if f.endswith('.json')])
        else:
            export_count = 0
        st.metric("Exported Files", export_count)
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎲 Generate Random Personas", use_container_width=True):
            st.session_state.quick_action = "generate"
            st.rerun()
    
    with col2:
        if st.button("📋 Run Survey", use_container_width=True):
            if persona_count > 0:
                st.session_state.quick_action = "survey"
                st.rerun()
            else:
                st.error("No personas available. Generate or import personas first.")
    
    with col3:
        if st.button("📁 Export Data", use_container_width=True):
            if persona_count > 0:
                st.session_state.quick_action = "export"
                st.rerun()
            else:
                st.error("No personas available to export.")
    
    # Handle quick actions
    if hasattr(st.session_state, 'quick_action'):
        if st.session_state.quick_action == "generate":
            with st.spinner("Generating personas..."):
                generator = PersonaGenerator()
                personas = generator.generate_balanced_personas(10)
                for persona in personas:
                    st.session_state.database.save_persona(persona)
                st.success(f"Generated {len(personas)} personas!")
                del st.session_state.quick_action
                st.rerun()
        
        elif st.session_state.quick_action == "survey":
            st.info("Navigate to Survey Management to run surveys.")
            del st.session_state.quick_action
        
        elif st.session_state.quick_action == "export":
            st.info("Navigate to Analytics & Results to export data.")
            del st.session_state.quick_action
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if persona_count > 0:
        personas = st.session_state.database.get_all_personas()
        recent_personas = sorted(personas, key=lambda x: x.created_at, reverse=True)[:5]
        
        for persona in recent_personas:
            with st.expander(f"{persona.id} - {persona.role}"):
                st.write(f"**Description:** {persona.get_description()}")
                st.write(f"**Created:** {persona.created_at.strftime('%Y-%m-%d %H:%M')}")
                if persona.response_history:
                    st.write(f"**Surveys completed:** {len(persona.response_history)}")
    else:
        st.info("No personas created yet. Start by generating or importing personas.")

def show_persona_management():
    """Persona management page"""
    st.title("👥 Persona Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Personas", "🎲 Generate", "📥 Import", "➕ Create Manual"])
    
    with tab1:
        show_persona_list()
    
    with tab2:
        show_persona_generation()
    
    with tab3:
        show_persona_import()
    
    with tab4:
        show_manual_persona_creation()

def show_persona_list():
    """Display list of all personas"""
    st.subheader("All Personas")
    
    personas = st.session_state.database.get_all_personas()
    
    if not personas:
        st.info("No personas found. Generate or import personas to get started.")
        return
    
    # Create DataFrame for display
    persona_data = []
    for persona in personas:
        persona_data.append({
            'ID': persona.id,
            'Role': persona.role,
            'Department': persona.department,
            'Gender': persona.gender,
            'Age Range': persona.age_range,
            'Experience': persona.experience,
            'Location': persona.location,
            'Team Size': persona.team_size,
            'Surveys': len(persona.response_history),
            'Created': persona.created_at.strftime('%Y-%m-%d')
        })
    
    df = pd.DataFrame(persona_data)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        role_filter = st.selectbox("Filter by Role", ["All"] + sorted(df['Role'].unique()))
    
    with col2:
        location_filter = st.selectbox("Filter by Location", ["All"] + sorted(df['Location'].unique()))
    
    with col3:
        department_filter = st.selectbox("Filter by Department", ["All"] + sorted(df['Department'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if role_filter != "All":
        filtered_df = filtered_df[filtered_df['Role'] == role_filter]
    if location_filter != "All":
        filtered_df = filtered_df[filtered_df['Location'] == location_filter]
    if department_filter != "All":
        filtered_df = filtered_df[filtered_df['Department'] == department_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Persona details
    if not filtered_df.empty:
        selected_id = st.selectbox("Select persona for details:", filtered_df['ID'].tolist())
        
        if selected_id:
            persona = st.session_state.database.get_persona(selected_id)
            if persona:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Persona Details")
                    st.write(f"**ID:** {persona.id}")
                    st.write(f"**Description:** {persona.get_description()}")
                    st.write(f"**Prompt Context:** {persona.get_prompt_context()}")
                
                with col2:
                    st.subheader("Survey History")
                    if persona.response_history:
                        for i, survey in enumerate(persona.response_history, 1):
                            with st.expander(f"Survey {i} - {survey['survey_id']}"):
                                st.write(f"**Timestamp:** {survey['timestamp']}")
                                st.write(f"**Responses:** {len(survey['responses'])}")
                                
                                # Show sample responses
                                for q_num, response in list(survey['responses'].items())[:3]:
                                    st.write(f"**Q{q_num}:** {response['response']}")
                    else:
                        st.info("No survey responses yet.")

def show_persona_generation():
    """Persona generation interface"""
    st.subheader("Generate Personas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        count = st.number_input("Number of personas to generate", min_value=1, max_value=100, value=10)
        balanced = st.checkbox("Generate balanced demographics", value=True)
    
    with col2:
        st.info("""
        **Balanced Generation:**
        - Ensures diverse representation across roles, departments, and demographics
        - Recommended for comprehensive surveys
        
        **Random Generation:**
        - Completely random demographic combinations
        - May result in less balanced representation
        """)
    
    if st.button("🎲 Generate Personas", type="primary"):
        with st.spinner(f"Generating {count} personas..."):
            generator = PersonaGenerator()
            
            if balanced:
                personas = generator.generate_balanced_personas(count)
            else:
                personas = generator.generate_personas(count)
            
            # Save to database
            for persona in personas:
                st.session_state.database.save_persona(persona)
            
            # Show summary
            summary = generator.get_demographics_summary(personas)
            
            st.success(f"✅ Generated {len(personas)} personas!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Generation Summary")
                st.write(f"**Total personas:** {summary['total_count']}")
                st.write(f"**Unique roles:** {len(summary['roles'])}")
                st.write(f"**Unique locations:** {len(summary['locations'])}")
                st.write(f"**Unique departments:** {len(summary['departments'])}")
            
            with col2:
                st.subheader("Role Distribution")
                role_df = pd.DataFrame(list(summary['roles'].items()), columns=['Role', 'Count'])
                st.bar_chart(role_df.set_index('Role'))
            
            st.session_state.personas_generated = True
def show_persona_import():
    """Persona import interface"""
    st.subheader("Import Personas")
    
    import_method = st.radio("Import method:", ["CSV Upload", "JSON Upload", "Download Template"])
    
    if import_method == "CSV Upload":
        st.write("Upload a CSV file with persona data")
        
        # Show expected format
        with st.expander("📋 CSV Format Requirements"):
            st.write("""
            Required columns:
            - **id**: Unique identifier (e.g., PM_001)
            - **role**: Job title (e.g., Product Manager)
            - **department**: Department (e.g., Product, Engineering)
            - **gender**: Male, Female, or Non-binary
            - **age_range**: 25-34, 35-44, 45-54, or 55-64
            - **experience**: 2-5 years, 5-10 years, Over 10 years, or Over 15 years
            - **location**: Country/region (e.g., USA, Germany)
            - **team_size**: 0-5, 5-10, 10-20, or Over 20 employees
            """)
        
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_file = f"temp_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Preview data
            df = pd.read_csv(temp_file)
            st.subheader("Preview")
            st.dataframe(df.head())
            
            if st.button("Import CSV Data"):
                with st.spinner("Importing personas..."):
                    try:
                        importer = PersonaImporter(Settings.DATABASE_PATH)
                        personas = importer.import_from_csv(temp_file)
                        
                        st.success(f"✅ Successfully imported {len(personas)} personas!")
                        
                        # Show import summary
                        summary = importer.get_import_summary()
                        st.write(f"**Total personas in database:** {summary['total_personas']}")
                        st.write(f"**Import sources:** {summary['import_sources']}")
                        
                    except Exception as e:
                        st.error(f"Import failed: {e}")
                    finally:
                        # Cleanup temp file
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
    
    elif import_method == "Download Template":
        st.write("Download a CSV template to fill with your persona data")
        
        if st.button("📥 Generate Template"):
            importer = PersonaImporter(Settings.DATABASE_PATH)
            template_file = importer.create_csv_template("persona_template.csv")
            
            # Read template for download
            with open(template_file, 'r') as f:
                template_content = f.read()
            
            st.download_button(
                label="📁 Download CSV Template",
                data=template_content,
                file_name="persona_template.csv",
                mime="text/csv"
            )
            
            st.success("Template generated! Fill it with your persona data and upload using CSV Upload.")

def show_manual_persona_creation():
    """Manual persona creation interface"""
    st.subheader("Create Individual Persona")
    
    with st.form("manual_persona_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            persona_id = st.text_input("Persona ID*", placeholder="e.g., PM_CUSTOM_001")
            role = st.text_input("Role/Job Title*", placeholder="e.g., Product Manager")
            department = st.selectbox("Department*", [
                "Product", "Engineering", "Marketing", "Sales", "Operations",
                "Human Resources", "Finance", "Design", "Data Science", "IT"
            ])
            gender = st.selectbox("Gender*", ["Male", "Female", "Non-binary"])
        
        with col2:
            age_range = st.selectbox("Age Range*", ["25-34", "35-44", "45-54", "55-64"])
            experience = st.selectbox("Experience*", [
                "2-5 years", "5-10 years", "Over 10 years", "Over 15 years"
            ])
            location = st.text_input("Location*", placeholder="e.g., USA, Germany, Canada")
            team_size = st.selectbox("Team Size*", [
                "0-5 employees", "5-10 employees", "10-20 employees", "Over 20 employees"
            ])
        
        submitted = st.form_submit_button("➕ Create Persona", type="primary")
        
        if submitted:
            # Validate required fields
            if not all([persona_id, role, department, gender, age_range, experience, location, team_size]):
                st.error("All fields are required!")
            else:
                try:
                    persona_data = {
                        'id': persona_id,
                        'role': role,
                        'department': department,
                        'gender': gender,
                        'age_range': age_range,
                        'experience': experience,
                        'location': location,
                        'team_size': team_size
                    }
                    
                    importer = PersonaImporter(Settings.DATABASE_PATH)
                    persona = importer.create_persona_manually(persona_data)
                    
                    st.success(f"✅ Created persona: {persona.id}")
                    st.write(f"**Description:** {persona.get_description()}")
                    st.write(f"**Prompt:** {persona.get_prompt_context()}")
                    
                except Exception as e:
                    st.error(f"Failed to create persona: {e}")

def show_survey_management():
    """Survey management page"""
    st.title("📊 Survey Management")
    
    tab1, tab2, tab3 = st.tabs(["📋 Survey Questions", "🚀 Run Survey", "📈 Survey Status"])
    
    with tab1:
        show_survey_questions()
    
    with tab2:
        show_run_survey()
    
    with tab3:
        show_survey_status()

def show_survey_questions():
    """Display survey questions"""
    st.subheader("Survey Questions")
    
    try:
        questions = SurveyQuestions(Settings.SURVEY_FILE)
        summary = questions.get_survey_summary()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Questions", summary['total_questions'])
        
        with col2:
            st.metric("Question Types", len(summary['question_types']))
        
        with col3:
            st.metric("Question Numbers", f"{min(summary['question_numbers'])}-{max(summary['question_numbers'])}")
        
        # Question type distribution
        st.subheader("Question Type Distribution")
        type_df = pd.DataFrame(list(summary['question_types'].items()), columns=['Type', 'Count'])
        fig = px.pie(type_df, values='Count', names='Type', title="Question Types")
        st.plotly_chart(fig, use_container_width=True)
        
        # Display all questions
        st.subheader("All Questions")
        
        for question in questions.get_questions():
            with st.expander(f"Q{question['question']}: {question['text'][:60]}..."):
                st.write(f"**Full Question:** {question['text']}")
                st.write(f"**Type:** {question['type']}")
                
                if 'options' in question:
                    st.write(f"**Options:** {', '.join(question['options'])}")
    
    except Exception as e:
        st.error(f"Error loading survey questions: {e}")
        st.info("Make sure survey.json file exists and is properly formatted.")

def show_run_survey():
    """Survey execution interface"""
    st.subheader("Run Survey")
    
    personas = st.session_state.database.get_all_personas()
    
    if not personas:
        st.warning("No personas available. Please generate or import personas first.")
        return
    
    # Check API configuration
    try:
        Settings.validate()
        api_configured = True
    except:
        api_configured = False
        st.error("OpenAI API key not configured. Please set it in the Settings page.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Available personas:** {len(personas)}")
        
        # Survey options
        survey_mode = st.radio("Survey mode:", ["Test (3 questions)", "Full Survey"])
        
        if survey_mode == "Test (3 questions)":
            persona_limit = st.selectbox("Test with persona:", [p.id for p in personas[:5]])
        else:
            persona_limit = st.number_input(
                "Limit personas (0 = all)", 
                min_value=0, 
                max_value=len(personas), 
                value=0
            )
    
    with col2:
        st.info("""
        **Test Mode:**
        - Runs first 3 questions only
        - Good for testing API connection
        - Quick validation of persona responses
        
        **Full Survey:**
        - Runs all 18 questions
        - Takes longer but provides complete data
        - Recommended for final data collection
        """)
    
    # Cost estimation
    if survey_mode == "Full Survey":
        estimated_personas = len(personas) if persona_limit == 0 else persona_limit
        estimated_cost = estimated_personas * 18 * 0.003  # Rough estimate
        st.write(f"**Estimated cost:** ~${estimated_cost:.2f}")
    
    if st.button("🚀 Start Survey", type="primary"):
        if survey_mode == "Test (3 questions)":
            run_test_survey(persona_limit)
        else:
            run_full_survey(persona_limit if persona_limit > 0 else None)

def show_survey_status():
    """Show survey completion status"""
    st.subheader("Survey Status")
    
    personas = st.session_state.database.get_all_personas()
    
    if not personas:
        st.info("No personas available.")
        return
    
    # Calculate statistics
    total_personas = len(personas)
    completed_surveys = len([p for p in personas if p.response_history])
    completion_rate = (completed_surveys / total_personas) * 100 if total_personas > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Personas", total_personas)
    
    with col2:
        st.metric("Completed Surveys", completed_surveys)
    
    with col3:
        st.metric("Completion Rate", f"{completion_rate:.1f}%")

def show_analytics():
    """Analytics and results page"""
    st.title("📈 Analytics & Results")
    
    tab1, tab2, tab3 = st.tabs(["📊 Demographics", "📁 Export Data", "🗄️ Research Archive"])
    
    with tab1:
        show_demographics_analytics()
    
    with tab2:
        show_export_interface()
    
    with tab3:
        show_research_archive()

def show_demographics_analytics():
    """Show demographic analytics"""
    st.subheader("Demographics Analysis")
    
    personas = st.session_state.database.get_all_personas()
    
    if not personas:
        st.info("No personas available for analysis.")
        return
    
    # Create demographics DataFrame
    demo_data = []
    for persona in personas:
        demo_data.append({
            'Role': persona.role,
            'Department': persona.department,
            'Gender': persona.gender,
            'Age Range': persona.age_range,
            'Experience': persona.experience,
            'Location': persona.location,
            'Team Size': persona.team_size,
            'Has Survey': len(persona.response_history) > 0
        })
    
    df = pd.DataFrame(demo_data)
    
    # Demographics charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Role distribution
        role_counts = df['Role'].value_counts()
        fig = px.bar(x=role_counts.index, y=role_counts.values, title="Role Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Location distribution
        location_counts = df['Location'].value_counts()
        fig = px.pie(values=location_counts.values, names=location_counts.index, title="Location Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_export_interface():
    """Data export interface"""
    st.subheader("Export Data")
    
    personas = st.session_state.database.get_all_personas()
    
    if not personas:
        st.info("No personas available to export.")
        return
    
    st.write(f"**Available personas:** {len(personas)}")
    
    export_limit = st.number_input("Limit export (0 = all)", min_value=0, max_value=len(personas), value=0)
    
    if st.button("📁 Export All Formats", type="primary"):
        with st.spinner("Exporting data..."):
            try:
                # Limit personas if specified
                export_personas = personas[:export_limit] if export_limit > 0 else personas
                
                # Get survey results
                survey_results = []
                for persona in export_personas:
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
                
                # Export data
                exporter = DataExporter(Settings.OUTPUT_DIR, Settings.PERSONAS_DIR)
                exported_files = exporter.export_all_formats(export_personas, survey_results)
                
                st.success(f"✅ Exported {len(export_personas)} personas!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Individual Files:**")
                    st.write(f"JSON files: {len(exported_files['individual_json'])}")
                    st.write(f"CSV files: {len(exported_files['individual_csv'])}")
                
                with col2:
                    st.write("**Master Files:**")
                    st.write(f"Master JSON: {len(exported_files['master_json'])}")
                    st.write(f"Analysis CSV: {len(exported_files['analysis_csv'])}")
                
            except Exception as e:
                st.error(f"Export failed: {e}")

def show_settings():
    """Settings and configuration page"""
    st.title("⚙️ Settings & Configuration")
    
    tab1, tab2 = st.tabs(["🔑 API Configuration", "📊 System Info"])
    
    with tab1:
        st.subheader("OpenAI API Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
        
        if api_key:
            # Save to environment (temporary for session)
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("API key set for this session!")
            
            # Test connection
            if st.button("🧪 Test API Connection"):
                with st.spinner("Testing connection..."):
                    try:
                        client = GPTClient()
                        if client.test_connection():
                            st.success("✅ API connection successful!")
                        else:
                            st.error("❌ API connection failed!")
                    except Exception as e:
                        st.error(f"❌ API test failed: {e}")
        
        st.info("""
        **Note:** For permanent configuration, add your API key to `config/.env`:
        ```
        OPENAI_API_KEY=your_api_key_here
        ```
        """)
    
    with tab2:
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Configuration:**")
            st.write(f"Model: {Settings.OPENAI_MODEL}")
            st.write(f"Max tokens: {Settings.MAX_TOKENS}")
            st.write(f"Temperature: {Settings.TEMPERATURE}")
            st.write(f"Rate limit: {Settings.REQUESTS_PER_SECOND} req/sec")
        
        with col2:
            st.write("**Paths:**")
            st.write(f"Database: {Settings.DATABASE_PATH}")
            st.write(f"Survey file: {Settings.SURVEY_FILE}")
            st.write(f"Output dir: {Settings.OUTPUT_DIR}")
            st.write(f"Personas dir: {Settings.PERSONAS_DIR}")

def run_test_survey(persona_id):
    """Run test survey for single persona"""
    persona = st.session_state.database.get_persona(persona_id)
    
    if not persona:
        st.error("Persona not found!")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        engine = SurveyEngine(Settings.SURVEY_FILE, Settings.DATABASE_PATH)
        
        status_text.text(f"Testing survey with {persona.id}...")
        
        result = engine.test_single_persona(persona, question_limit=3)
        
        progress_bar.progress(100)
        status_text.text("Test completed!")
        
        st.success("✅ Test survey completed!")
        
        # Show results
        st.subheader("Test Results")
        st.write(f"**Persona:** {persona.id}")
        st.write(f"**Completion time:** {result['completion_time_seconds']:.1f} seconds")
        st.write(f"**Questions tested:** {result['questions_tested']}")
        
        # Show responses
        for q_num, response_data in result['test_responses'].items():
            with st.expander(f"Q{q_num}: {response_data['question'][:50]}..."):
                st.write(f"**Question:** {response_data['question']}")
                st.write(f"**Response:** {response_data['response']}")
                st.write(f"**Type:** {response_data['type']}")
    
    except Exception as e:
        st.error(f"Test survey failed: {e}")

def run_full_survey(persona_limit):
    """Run full survey for all or limited personas"""
    personas = st.session_state.database.get_all_personas()
    
    if persona_limit:
        personas = personas[:persona_limit]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()
    
    try:
        engine = SurveyEngine(Settings.SURVEY_FILE, Settings.DATABASE_PATH)
        
        results = []
        total_personas = len(personas)
        
        for i, persona in enumerate(personas):
            progress = (i + 1) / total_personas
            progress_bar.progress(progress)
            status_text.text(f"Surveying {persona.id} ({i+1}/{total_personas})...")
            
            result = engine.run_survey_for_persona(persona)
            results.append(result)
            
            # Update results display
            with results_container.container():
                st.write(f"**Completed:** {i+1}/{total_personas}")
                if result.get('error'):
                    st.error(f"❌ {persona.id}: {result['error']}")
                else:
                    st.success(f"✅ {persona.id}: {result['successful_responses']}/{result['total_questions']} responses")
        
        # Final statistics
        stats = engine.get_survey_statistics(results)
        
        st.success("🎉 Survey completed!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
        
        with col2:
            st.metric("Total Time", f"{stats['total_time_seconds']:.1f}s")
        
        with col3:
            st.metric("Avg per Persona", f"{stats['average_time_per_persona']:.1f}s")
        
        st.session_state.survey_completed = True
        
    except Exception as e:
        st.error(f"Survey failed: {e}")
def show_research_archive():
    """Research archive management interface"""
    st.subheader("Research Archive Management")
    
    # Import the research archiver
    from research import ResearchArchiver
    
    # Create tabs for different archive operations
    archive_tab1, archive_tab2, archive_tab3 = st.tabs(["📦 Archive Current", "📋 View Archives", "🔄 Restore Archive"])
    
    with archive_tab1:
        st.subheader("Archive Current Research")
        
        personas = st.session_state.database.get_all_personas()
        
        if not personas:
            st.info("No research data to archive. Generate or import personas first.")
        else:
            st.write(f"**Current research data:**")
            st.write(f"- Personas: {len(personas)}")
            completed_surveys = len([p for p in personas if p.response_history])
            st.write(f"- Completed surveys: {completed_surveys}")
            
            with st.form("archive_form"):
                research_name = st.text_input("Research Name*", placeholder="e.g., AI_Adoption_Study_2025")
                description = st.text_area("Description", placeholder="Brief description of this research...")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    archive_only = st.form_submit_button("📦 Archive Only", type="secondary")
                
                with col2:
                    archive_and_clear = st.form_submit_button("📦 Archive & Clear", type="primary")
                
                if archive_only and research_name:
                    with st.spinner("Creating archive..."):
                        try:
                            archiver = ResearchArchiver()
                            result = archiver.create_archive(research_name, description)
                            
                            st.success("✅ Research archived successfully!")
                            st.write(f"**Archive:** {result['archive_name']}")
                            st.write(f"**Location:** {result['archive_path']}")
                            st.write(f"**Personas:** {result['personas_count']}")
                            st.write(f"**Surveys:** {result['surveys_count']}")
                            
                        except Exception as e:
                            st.error(f"Archive failed: {e}")
                
                elif archive_and_clear and research_name:
                    st.warning("⚠️ This will archive current data and clear the database for new research!")
                    
                    if st.checkbox("I understand this will clear all current data"):
                        with st.spinner("Archiving and clearing..."):
                            try:
                                archiver = ResearchArchiver()
                                result = archiver.archive_and_clear(research_name, description)
                                
                                st.success("🎉 Research archived and system cleared!")
                                st.write(f"**Archive:** {result['archive_name']}")
                                st.write(f"**Archived:** {result['archived_personas']} personas, {result['archived_surveys']} surveys")
                                st.write(f"**Cleared:** {result['cleared_personas']} personas")
                                st.info("System is now ready for new research!")
                                
                                # Refresh the page to show empty state
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Archive and clear failed: {e}")
                
                elif (archive_only or archive_and_clear) and not research_name:
                    st.error("Please enter a research name")
    
    with archive_tab2:
        st.subheader("Available Archives")
        
        try:
            archiver = ResearchArchiver()
            archives = archiver.list_archives()
            
            if not archives:
                st.info("No research archives found.")
            else:
                st.write(f"Found {len(archives)} research archives:")
                
                for archive in archives:
                    with st.expander(f"📁 {archive['research_name']} ({archive['created_at'][:10]})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Archive Name:** {archive['archive_name']}")
                            st.write(f"**Created:** {archive['created_at']}")
                            st.write(f"**Personas:** {archive['personas_count']}")
                            st.write(f"**Surveys:** {archive['surveys_count']}")
                        
                        with col2:
                            if archive['description']:
                                st.write(f"**Description:** {archive['description']}")
                            st.write(f"**Location:** {archive['archive_path']}")
                        
                        # Quick restore button
                        if st.button(f"🔄 Restore {archive['research_name']}", key=f"restore_{archive['archive_name']}"):
                            st.session_state.restore_archive = archive['archive_name']
                            st.rerun()
        
        except Exception as e:
            st.error(f"Error loading archives: {e}")
    
    with archive_tab3:
        st.subheader("Restore Research Archive")
        
        # Handle restore action from archive list
        if hasattr(st.session_state, 'restore_archive'):
            archive_name = st.session_state.restore_archive
            del st.session_state.restore_archive
            
            st.warning(f"⚠️ Restoring '{archive_name}' will overwrite all current research data!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Confirm Restore", type="primary"):
                    with st.spinner("Restoring research..."):
                        try:
                            archiver = ResearchArchiver()
                            result = archiver.restore_archive(archive_name)
                            
                            st.success("🎉 Research restored successfully!")
                            st.write(f"**Archive:** {result['archive_name']}")
                            st.write(f"**Restored:** {result['restored_personas']} personas")
                            st.info("Research data is now active!")
                            
                            # Refresh to show restored data
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Restore failed: {e}")
            
            with col2:
                if st.button("❌ Cancel"):
                    st.rerun()
        
        else:
            # Manual restore interface
            try:
                archiver = ResearchArchiver()
                archives = archiver.list_archives()
                
                if not archives:
                    st.info("No archives available to restore.")
                else:
                    archive_names = [f"{a['research_name']} ({a['archive_name']})" for a in archives]
                    selected = st.selectbox("Select archive to restore:", [""] + archive_names)
                    
                    if selected:
                        # Extract archive name from selection
                        archive_name = selected.split("(")[1].rstrip(")")
                        
                        st.warning("⚠️ This will overwrite all current research data!")
                        
                        if st.button("🔄 Restore Selected Archive", type="primary"):
                            if st.checkbox("I understand this will overwrite current data"):
                                with st.spinner("Restoring research..."):
                                    try:
                                        result = archiver.restore_archive(archive_name)
                                        
                                        st.success("🎉 Research restored successfully!")
                                        st.write(f"**Archive:** {result['archive_name']}")
                                        st.write(f"**Restored:** {result['restored_personas']} personas")
                                        
                                        # Refresh to show restored data
                                        st.rerun()
                                        
                                    except Exception as e:
                                        st.error(f"Restore failed: {e}")
            
            except Exception as e:
                st.error(f"Error loading archives: {e}")
if __name__ == "__main__":
    main()