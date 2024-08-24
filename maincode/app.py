from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()

app = Flask(__name__)

# Replace with your OpenRouter API key or set it in your .env file
#OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENROUTER_API_KEY="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"
PROFESSORS_FILE = 'professors.json'

# Load professor data from the JSON file
def load_professors():
    try:
        with open(PROFESSORS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

# Initialize professors list
professors = load_professors()

@app.route('/')
def index():
    return render_template('index.html', professors=professors)



@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if not query:
        return redirect(url_for('index'))

    # Prepare the AI query including the professor data
    prompt = (
        f"Find a professor who matches this criteria: {query}. Here is the data:\n"
        f"{json.dumps(professors, indent=2)}"
    )

    # Make a request to OpenRouter API
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses

        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            message = data['choices'][0]['message']['content']
            return render_template('results.html', message=message)
        else:
            return "No relevant results found.", 404
    except requests.RequestException as e:
        return f"Error fetching data from OpenRouter API: {e}", 500
    
@app.route('/submit_professor', methods=['POST'])
def submit_professor():
    # Get form data
    name = request.form['name']
    university = request.form['university']
    subject = request.form['subject']
    speciality = request.form['speciality']
    rating = float(request.form['rating'])  # Convert rating to float

    # Create a new professor dictionary
    new_professor = {
        "name": name,
        "university": university,
        "subject": subject,
        "speciality": speciality,
        "rating": rating  # Store as float
    }


    # Append the new professor to the list and write it back to the JSON file
    professors.append(new_professor)

    with open(PROFESSORS_FILE, 'w') as file:
        json.dump(professors, file, indent=4)

    return redirect(url_for('index'))


@app.route('/professors')
def show_professors():
    with open(PROFESSORS_FILE, 'r') as file:
        professors = json.load(file)
    return render_template('professors.html', professors=professors)

if __name__ == '__main__':
    app.run()
