I created VocaBoost as a personal side project when my existing vocabulary learning app was about to expire and didn't fully meet my needs. I wanted a customizable solution that would combine dictionary lookups, smart review scheduling, and AI-generated examples - all in one application that I could extend as needed.
Feel free to use it.

# VocaBoost - Vocabulary Learning Application

VocaBoost is a Flask-based web application designed to help users expand their vocabulary through spaced repetition learning. It provides dictionary lookups, example sentences, and a systematic review system to improve vocabulary retention.

## Features

- **Dictionary Lookup**: Search for word definitions, example sentences, and pronunciations
- **AI-Generated Examples**: For words without examples, the app generates natural-sounding sentences using Google's Gemini AI
- **Spaced Repetition System**: Words are scheduled for review at optimized intervals based on your recall performance
- **Progress Tracking**: Monitor your vocabulary learning progress with different memory levels
- **Word Organization**: Words are grouped by their memory level, from new to mastered
- **Part of Speech Grouping**: Definitions are organized by part of speech (noun, verb, adjective, etc.)
- **Audio Pronunciation**: Listen to correct pronunciations for words (when available)

## Installation

1. Clone the repository:
```bash
git clone <repository-url> cd Vocaboost
```
2. Create and activate a virtual environment:
```bash
python -m venv venv source venv/bin/activate # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Set up environment variables:
```bash
cp .env.example .env
```
Edit the `.env` file and add your Gemini API key. You can get one from [Google AI Studio](https://aistudio.google.com/apikey).
5. Initialize the database:
```bash
python reset_db.py
```
6. Run the application:
```bash
python app.py
```

7. Visit `http://localhost:5000` in your browser to use the application.

## Usage

1. **Search for Words**: Enter a word in the search box and click "Search" to see definitions
2. **Save Words**: Click "Save" to add a word to your vocabulary list
3. **Review Words**: Click "Review" to practice words that are due for review
4. **View All Words**: Click "My Words" to see all saved words organized by memory level
5. **Delete Words**: Click the trash icon on a word card to remove it

## Technologies Used

- **Flask**: Web framework
- **SQLAlchemy**: ORM for database interactions
- **Google Gemini API**: For generating example sentences
- **Bootstrap**: Frontend styling
- **JavaScript**: Interactive elements

## Project Structure

- `app.py`: Main application file
- `vocaboost/models/`: Database models
- `vocaboost/services/`: External API integrations
- `vocaboost/templates/`: HTML templates
- `vocaboost/static/`: CSS, JavaScript, and other static files

## Acknowledgments

- [Free Dictionary API](https://dictionaryapi.dev/) for providing word definitions
- Google's Gemini API for generating example sentences
