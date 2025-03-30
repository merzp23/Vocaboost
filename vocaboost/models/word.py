from datetime import datetime
from vocaboost.database.db import db
import json

class Word(db.Model):
    """Model for saved vocabulary words"""
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False, unique=True)
    
    # Word data from API
    definition = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text, nullable=True)
    phonetic = db.Column(db.String(100), nullable=True)
    audio_url = db.Column(db.String(255), nullable=True)
    
    # Raw API response for future use
    api_data = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Progress
    progress = db.relationship('Progress', backref='word', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Word {self.text}>'
    
    @staticmethod
    def save_from_api(api_data):
        """Create or update a word from API data"""
        if not api_data or len(api_data) == 0:
            return None
            
        word_data = api_data[0]
        
        # Find existing or create new
        word = Word.query.filter_by(text=word_data['word']).first()
        if not word:
            word = Word(text=word_data['word'])
        
        # Set basic properties
        first_definition = ""
        first_example = ""
        
        # Extract first definition and example
        if 'meanings' in word_data and len(word_data['meanings']) > 0:
            meaning = word_data['meanings'][0]
            if 'definitions' in meaning and len(meaning['definitions']) > 0:
                first_definition = meaning['definitions'][0]['definition']
                if 'example' in meaning['definitions'][0]:
                    first_example = meaning['definitions'][0]['example']
        
        # Set audio URL if available
        audio_url = ""
        if 'phonetics' in word_data:
            for phonetic in word_data['phonetics']:
                if 'audio' in phonetic and phonetic['audio']:
                    audio_url = phonetic['audio']
                    break
        
        # Update word data
        word.definition = first_definition
        word.example = first_example
        word.phonetic = word_data.get('phonetic', '')
        word.audio_url = audio_url
        word.api_data = json.dumps(word_data)
        
        # Save to database
        db.session.add(word)
        db.session.commit()
        
        return word