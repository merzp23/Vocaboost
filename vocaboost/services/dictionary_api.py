import requests
from vocaboost.services.gemini_api import GeminiService

class DictionaryService:
    """Service for fetching word definitions from the Dictionary API"""
    
    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"
    
    @classmethod
    def get_definition(cls, word):
        """
        Fetch definition for a word from the Dictionary API
        
        Args:
            word (str): The word to look up
            
        Returns:
            dict: Word data or None if not found
        """
        if not word:
            return None
            
        try:
            response = requests.get(f"{cls.BASE_URL}/{word.lower().strip()}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching definition: {e}")
            return None
    @classmethod
    def enrich_with_examples(cls, word_data):
        """Add AI-generated examples to definitions that don't have them"""
        if not word_data:
            return word_data
            
        # Track if any examples were generated
        examples_generated = False
            
        # Process each meaning
        for meaning in word_data[0].get('meanings', []):
            part_of_speech = meaning.get('partOfSpeech', '')
            
            # Process each definition
            for definition in meaning.get('definitions', []):
                # Skip if it already has an example
                if 'example' in definition and definition['example']:
                    continue
                    
                # Generate example
                generated_example = GeminiService.generate_example(
                    word_data[0].get('word', ''),
                    definition.get('definition', ''),
                    part_of_speech
                )
                
                if generated_example:
                    definition['example'] = generated_example
                    # Add a flag to mark AI-generated examples
                    definition['example_is_generated'] = True
                    examples_generated = True
        
        return word_data