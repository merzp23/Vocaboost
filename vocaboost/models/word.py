from datetime import datetime
from vocaboost.database.db import db
from vocaboost.models.definition import Definition
import json
from vocaboost.services.gemini_api import GeminiService
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
    
    # Relationships
    progress = db.relationship('Progress', backref='word', lazy=True, cascade="all, delete-orphan")
    definitions = db.relationship('Definition', backref='word', lazy=True, 
                                 cascade="all, delete-orphan", order_by="Definition.display_order")
    
    def __repr__(self):
        return f'<Word {self.text}>'
    
    @staticmethod
    def save_from_api(api_data):
        """Create or update a word from API data"""
        if not api_data or len(api_data) == 0:
            return None
            
        word_data = api_data[0]
        print(f"Processing word: {word_data.get('word', 'unknown')}")
        
        # Find existing or create new
        word = Word.query.filter_by(text=word_data['word']).first()
        if not word:
            word = Word(text=word_data['word'])
            print(f"Creating new word: {word_data['word']}")
        else:
            print(f"Updating existing word: {word_data['word']}")
        
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
        
        # Save to database to ensure we have an ID
        db.session.add(word)
        db.session.commit()
        
        # Remove existing definitions
        if word.definitions:
            print(f"Deleting {len(word.definitions)} existing definitions")
            Definition.query.filter_by(word_id=word.id).delete()
            db.session.commit()
        
        # Add all definitions from the API data
        display_order = 0  # Initialize display_order here
        definitions_added = 0
        
        if 'meanings' in word_data:
            for meaning_index, meaning in enumerate(word_data['meanings']):
                part_of_speech = meaning.get('partOfSpeech', 'unknown')
                
                if 'definitions' in meaning:
                    for def_index, def_data in enumerate(meaning['definitions']):
                        try:
                            definition_text = def_data.get('definition', '')
                            example_text = def_data.get('example', '')
                            
                            # IMPORTANT: Track if we generate an example
                            is_generated = False
                            
                            # Generate an example if none exists
                            if not example_text:
                                print(f"No example found for '{word.text}' ({part_of_speech}), generating one...")
                                generated_example = GeminiService.generate_example(
                                    word.text,
                                    definition_text,
                                    part_of_speech
                                )
                                if generated_example:
                                    example_text = generated_example
                                    is_generated = True  # Set this flag when we generate an example
                                    print(f"Generated example: {example_text}")
                            
                            # Create definition with the correct flag
                            definition = Definition(
                                word_id=word.id,
                                part_of_speech=part_of_speech,
                                text=definition_text,
                                example=example_text,
                                synonyms=json.dumps(def_data.get('synonyms', [])) if def_data.get('synonyms') else None,
                                antonyms=json.dumps(def_data.get('antonyms', [])) if def_data.get('antonyms') else None,
                                display_order=display_order,
                                example_is_generated=is_generated  # Make sure this gets set
                            )
                            display_order += 1
                            definitions_added += 1
                            db.session.add(definition)
                        except Exception as e:
                            print(f"Error adding definition: {e}")
        
        print(f"Added {definitions_added} definitions for '{word.text}'")
        db.session.commit()
        return word
    # Add this method to the Word class
    def get_definitions_by_type(self):
        """Group definitions by part of speech"""
        grouped = {}
        
        # First try to use the definitions relationship
        if hasattr(self, 'definitions') and self.definitions:
            for definition in self.definitions:
                pos = definition.part_of_speech
                if pos not in grouped:
                    grouped[pos] = []
                grouped[pos].append(definition)
        
        # If no definitions found but we have API data, try parsing that
        elif self.api_data:
            try:
                data = json.loads(self.api_data)
                if data and len(data) > 0 and 'meanings' in data[0]:
                    for meaning in data[0]['meanings']:
                        pos = meaning.get('partOfSpeech', 'unknown')
                        if pos not in grouped:
                            grouped[pos] = []
                        
                        if 'definitions' in meaning:
                            for def_data in meaning['definitions']:
                                # Create a simple object to mimic Definition
                                definition = type('Definition', (), {
                                    'part_of_speech': pos,
                                    'text': def_data.get('definition', ''),
                                    'example': def_data.get('example', ''),
                                    'get_synonyms': lambda: def_data.get('synonyms', []),
                                    'get_antonyms': lambda: def_data.get('antonyms', [])
                                })
                                grouped[pos].append(definition)
            except:
                # Fallback to empty if JSON parsing fails
                pass
        
        return grouped