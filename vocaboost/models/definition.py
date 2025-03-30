from vocaboost.database.db import db
import json

class Definition(db.Model):
    """Model for individual word definitions"""
    __tablename__ = 'definitions'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    
    # Definition data
    part_of_speech = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)  # The actual definition text
    example = db.Column(db.Text, nullable=True)
    example_is_generated = db.Column(db.Boolean, default=False)
    # Optional extras
    synonyms = db.Column(db.Text, nullable=True)  # Stored as JSON string
    antonyms = db.Column(db.Text, nullable=True)  # Stored as JSON string
    
    # Order within a word's definitions
    display_order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Definition {self.part_of_speech}: {self.text[:30]}...>'
        
    def get_synonyms(self):
        """Get synonyms as a list"""
        if self.synonyms:
            try:
                return json.loads(self.synonyms)
            except:
                return []
        return []
        
    def get_antonyms(self):
        """Get antonyms as a list"""
        if self.antonyms:
            try:
                return json.loads(self.antonyms)
            except:
                return []
        return []