from flask import Flask, render_template, request, jsonify
from vocaboost.services.dictionary_api import DictionaryService
from vocaboost.database.db import init_app as init_db
from vocaboost.models.word import Word
from vocaboost.models.progress import Progress
import json

def create_app():
    app = Flask(__name__, 
                template_folder='vocaboost/templates',
                static_folder='vocaboost/static')
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vocaboost.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        word_data = None
        search_term = ""
        
        if request.method == 'POST':
            search_term = request.form.get('search', '').strip()
            if search_term:
                word_data = DictionaryService.get_definition(search_term)
        
        return render_template('index.html', word_data=word_data, search_term=search_term)
    
    @app.route('/save-word', methods=['POST'])
    def save_word():
        try:
            data = request.get_json()
            api_data = json.loads(data.get('data')) if data.get('data') else None
            
            if not api_data:
                return jsonify({'success': False, 'error': 'Invalid word data'})
            
            # Save word to database
            word = Word.save_from_api(api_data)
            
            # Create initial progress
            Progress.create_for_word(word.id)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)