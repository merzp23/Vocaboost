import requests

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