import google.generativeai as genai

genai.configure(api_key="AIzaSyCzaDN3mv5oHJLw6FCWRnrZkKGxkLYgA3E")  # Replace with your actual API key

# List available models
for model in genai.list_models():
    print(f"{model.name} -> {model.supported_generation_methods}")
