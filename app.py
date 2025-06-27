from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import re
from scripts import scraper 
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("key") #replace with whatever

# --- Helper Functions ---

# Load museum data from the JSON file
def load_museum_data():
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'output', 'output_final.json') 
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Please ensure 'output_final.json' is in the 'output' directory.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. Check if the JSON is valid.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred loading data from {file_path}: {e}")
        return {}


# Extract unique states, themes, and ownerships for dropdowns
def get_unique_options(data):
    states = sorted(list(set(m.get('state/ut', 'N/A') for m in data.values())))
    themes = sorted(list(set(m.get('theme', 'N/A') for m in data.values())))
    ownerships = sorted(list(set(m.get('ownership', 'N/A') for m in data.values())))
    return states, themes, ownerships

# Function to sanitize museum names for valid filenames
def sanitize_filename(name):
    s = re.sub(r'[^\w\s-]', '', name)
    s = s.replace(' ', '_')
    s = s.strip('_')
    return s.lower()


# --- Global Data Initialization ---
museums_data = load_museum_data()
unique_states, unique_themes, unique_ownerships = get_unique_options(museums_data)


# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    filtered_museums = museums_data.copy()
    
    if 'staged_museum_ids' not in session:
        session['staged_museum_ids'] = []

    staged_museum_objects = []
    staged_ids_set = set(session['staged_museum_ids']) 
    for mid in staged_ids_set: 
        if mid in museums_data: 
            obj = museums_data[mid].copy()
            obj['id'] = mid 
            staged_museum_objects.append(obj)
    
    staged_museum_objects.sort(key=lambda x: x.get('name', ''))


    current_filters = {
        'name_filter': '',
        'state_filter': '',
        'theme_filter': '',
        'ownership_filter': '',
        'overview_keywords': ''
    }

    if request.method == 'POST':
        name_filter = request.form.get('name_filter', '').strip().lower()
        state_filter = request.form.get('state_filter', '').strip().lower()
        theme_filter = request.form.get('theme_filter', '').strip().lower()
        ownership_filter = request.form.get('ownership_filter', '').strip().lower()
        overview_keywords = request.form.get('overview_keywords', '').strip().lower()
        
        action_requested = request.form.get('action') 

        current_filters.update({
            'name_filter': request.form.get('name_filter', '').strip(),
            'state_filter': request.form.get('state_filter', '').strip(),
            'theme_filter': request.form.get('theme_filter', '').strip(),
            'ownership_filter': request.form.get('ownership_filter', '').strip(),
            'overview_keywords': request.form.get('overview_keywords', '').strip()
        })

        temp_filtered_museums = {}
        for museum_id, museum in filtered_museums.items():
            match = True

            museum_name = museum.get('name', '').lower()
            museum_state = museum.get('state/ut', '').lower()
            museum_theme = museum.get('theme', '').lower()
            museum_ownership = museum.get('ownership', '').lower()
            museum_overview = museum.get('overview', '').lower()
            
            if name_filter and name_filter not in museum_name:
                match = False
            
            if state_filter and state_filter != 'all' and state_filter != museum_state:
                match = False
            
            if theme_filter and theme_filter != 'all' and theme_filter != museum_theme:
                match = False

            if ownership_filter and ownership_filter != 'all' and ownership_filter != museum_ownership:
                match = False

            if overview_keywords:
                keywords_list = [k.strip() for k in overview_keywords.split() if k.strip()]
                if keywords_list:
                    if not all(keyword in museum_overview for keyword in keywords_list):
                        match = False
            
            if match:
                temp_filtered_museums[museum_id] = museum
        
        filtered_museums = temp_filtered_museums

        if action_requested == 'add_all':
            for museum_id in filtered_museums.keys():
                if museum_id not in session['staged_museum_ids']: 
                    session['staged_museum_ids'].append(museum_id)
            session.modified = True 
            
            staged_museum_objects = []
            staged_ids_set = set(session['staged_museum_ids']) 
            for mid in staged_ids_set:
                if mid in museums_data:
                    obj = museums_data[mid].copy()
                    obj['id'] = mid 
                    staged_museum_objects.append(obj)
            staged_museum_objects.sort(key=lambda x: x.get('name', '')) 

    return render_template('index.html', 
                           museums=filtered_museums, 
                           staging_area=staged_museum_objects, 
                           unique_states=unique_states,
                           unique_themes=unique_themes,
                           unique_ownerships=unique_ownerships,
                           current_filters=current_filters)

@app.route('/add_to_staging/<int:museum_id>')
def add_to_staging(museum_id):
    if museum_id in museums_data and museum_id not in session['staged_museum_ids']:
        session['staged_museum_ids'].append(museum_id)
        session.modified = True 
    return redirect(url_for('index'))

@app.route('/remove_from_staging/<int:museum_id>')
def remove_from_staging(museum_id):
    if museum_id in session['staged_museum_ids']:
        session['staged_museum_ids'].remove(museum_id)
        session.modified = True
    return redirect(url_for('index'))

@app.route('/clear_staging')
def clear_staging():
    session['staged_museum_ids'] = [] 
    session.modified = True
    return redirect(url_for('index'))

# UPDATED: Route to immediately show a processing page with staged museum names
@app.route('/start_processing')
def start_processing():
    museum_names_to_process = []
    for mid in session['staged_museum_ids']:
        if mid in museums_data:
            museum_names_to_process.append(museums_data[mid].get('name', 'Unknown Museum'))
    # Sort for consistent display
    museum_names_to_process.sort() 
    return render_template('processing_page.html', museums_to_process=museum_names_to_process)


@app.route('/perform_action_on_staging')
def perform_action_on_staging():
    museums_for_action = []
    for mid in session['staged_museum_ids']:
        if mid in museums_data:
            museums_for_action.append(museums_data[mid])

    action_details = [] 
    script_dir = os.path.dirname(__file__)
    reviews_dir_path = os.path.join(script_dir, 'reviews') 

    for museum in museums_for_action:
        museum_name = museum.get('name', 'Unknown Museum')
        museum_url = museum.get('maps_url', 'No Maps URL provided') 
        sanitized_name = sanitize_filename(museum_name)
        review_file_name = f"{sanitized_name}.json"
        review_file_path = os.path.join(reviews_dir_path, review_file_name)

        status_message = f"Processing '{museum_name}' (Maps URL: {museum_url}): "
        
        if os.path.exists(review_file_path):
            status_message += "Scraped review file already exists."
        else:
            status_message += "Scraped review file NOT found. Initiating scraping..."
            if scraper.scrape_maps_reviews(museum_url, review_file_path):
                status_message += " Scraping and saving reviews successful."
            else:
                status_message += " Failed to scrape and save reviews."
            
        action_details.append(status_message)
        
    session['staged_museum_ids'] = [] 
    session.modified = True

    return render_template('action_results.html', action_details=action_details)


if __name__ == '__main__':
    app.run(debug=True)