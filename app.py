from flask import Flask, render_template, request, jsonify
from vocaboost.services.dictionary_api import DictionaryService
from vocaboost.database.db import init_app as init_db
from vocaboost.models.word import Word
from vocaboost.models.progress import Progress
import json
from vocaboost.database.db import db


def create_app():
    app = Flask(__name__, 
                template_folder='vocaboost/templates',
                static_folder='vocaboost/static')
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vocaboost.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)

    @app.context_processor
    def inject_recent_words():
        """Make recent words available to all templates"""
        recent_words = Word.query.order_by(Word.created_at.desc()).limit(5).all()
        return dict(recent_words=recent_words)
    
    @app.template_filter('fromjson')
    def fromjson(value):
        """Parse a JSON string into a Python object for templates"""
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return None
    @app.route('/', methods=['GET', 'POST'])
    def index():
        word_data = None
        search_term = ""
        
        if request.method == 'POST':
            search_term = request.form.get('search', '').strip()
            if search_term:
                # Get the word data
                word_data = DictionaryService.get_definition(search_term)
                
                # Enrich with AI-generated examples
                if word_data:
                    word_data = DictionaryService.enrich_with_examples(word_data)
        
        # Get recently saved words for sidebar
        return render_template('index.html', 
                            word_data=word_data, 
                            search_term=search_term)
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
        
    @app.route('/review', methods=['GET'])
    def review():
        # Get words due for review with their progress
        due_words = Progress.get_due_words(limit=10)
        
        # Load the complete word for each progress item
        due_words_with_details = []
        for progress in due_words:
            word = Word.query.get(progress.word_id)
            if word:
                progress.word = word
                due_words_with_details.append(progress)
        
        return render_template('review.html', due_words=due_words_with_details)

    @app.route('/review-word', methods=['POST'])
    def review_word():
        try:
            data = request.get_json()
            word_id = data.get('word_id')
            recalled_correctly = data.get('recalled_correctly', False)
            
            progress = Progress.query.filter_by(word_id=word_id).first()
            if not progress:
                return jsonify({'success': False, 'error': 'Progress not found'})
                
            progress.update_review(recalled_correctly)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    #Delete a word
    @app.route('/delete-word/<int:word_id>', methods=['POST'])
    def delete_word(word_id):
        try:
            # Find the word
            word = Word.query.get_or_404(word_id)
            
            # Get the word text for confirmation message
            word_text = word.text
            
            # Delete the word (will cascade to definitions because of relationship)
            db.session.delete(word)
            db.session.commit()
            
            # Return JSON response
            return jsonify({'success': True, 'message': f'Word "{word_text}" deleted successfully'})
            
        except Exception as e:
            # Log the error
            print(f"Error deleting word: {str(e)}")
            
            # Return error response as JSON
            return jsonify({'success': False, 'error': str(e)})
        
    @app.route('/words', methods=['GET'])
    def words_by_level():
        """Display all saved words organized by memory level"""
        
        # Create a dictionary to store words by level
        words_by_level = {
            0: [], # New words
            1: [],
            2: [],
            3: [],
            4: [],
            5: []  # Mastered words
        }
        
        # Get all words with their progress
        words = Word.query.all()
        
        for word in words:
            # Get the progress for this word
            progress = Progress.query.filter_by(word_id=word.id).first()
            level = 0
            
            if progress:
                level = progress.memory_level
                # Add next review date
                word.next_review = progress.next_review_at
            else:
                word.next_review = None
                
            # Add word to the appropriate level list
            words_by_level[level].append(word)
        
        # Count total words
        total_words = sum(len(words) for words in words_by_level.values())
        
        return render_template('words.html', 
                            words_by_level=words_by_level,
                            total_words=total_words)
    return app
    
    # This must be the last line in create_app
    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)