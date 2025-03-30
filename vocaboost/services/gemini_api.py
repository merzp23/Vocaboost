import os
from dotenv import load_dotenv
from google import generativeai as genai

# Load environment variables from .env file
load_dotenv()

class GeminiService:
    """Service for interacting with Google's Gemini API"""
    
    API_KEY = os.getenv('GEMINI_API_KEY')
    
    @classmethod
    def generate_example(cls, word, definition, part_of_speech):
        """Generate a natural-sounding example sentence for a word"""
        if not cls.API_KEY:
            print("Cannot generate example: No API key configured")
            return None
        
        # Initialize the Gemini SDK with the API key
        # Note: We don't need a separate setup_client method anymore
        genai.configure(api_key=cls.API_KEY)
        
        prompt = f"""
        Create a natural-sounding example sentence using the word '{word}' as a {part_of_speech}.
        
        Definition: {definition}
        
        Return only the example sentence, with no additional explanation or notes.
        The sentence should be clear, concise, and demonstrate the meaning of the word correctly.
        """
        
        try:
            # Create a model instance
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Extract the text
            if response:
                example = response.text.strip()
                # Clean up any quotes
                example = example.strip('"\'')
                print(f"Generated example for '{word}': {example}")
                return example
            
            print("No valid response received from Gemini API")
            return None
            
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            return None