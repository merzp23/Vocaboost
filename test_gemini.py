from vocaboost.services.gemini_api import GeminiService

# Test with a simple example
word = "ephemeral"
definition = "lasting for a very short time"
part_of_speech = "adjective"

print(f"Testing Gemini API with word: {word}")
print(f"Definition: {definition}")
print(f"Part of speech: {part_of_speech}")
print("-" * 50)

# Try to generate an example
example = GeminiService.generate_example(word, definition, part_of_speech)

if example:
    print("✅ SUCCESS! Example generated:")
    print(f'"{example}"')
else:
    print("❌ ERROR: Could not generate example")
    print("Check your API key and network connection")