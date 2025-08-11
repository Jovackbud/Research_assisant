import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# --- Global variable to hold the model ---
generator_model = None
api_key_present = False # Flag to track if API key was found

try:
    # Configure the generative AI model
    api_key = os.getenv('google_ai_studio_key')

    if not api_key:
        logging.error("Google AI API key 'google_ai_studio_key' not found in .env file. Gemini model will not be available.")
    else:
        genai.configure(api_key=api_key)
        generator_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are an experienced doctoral research assistant. Your task is to extract specific information from research papers and provide it in a structured JSON format. Ensure all keys are in snake_case. If any information is unavailable, use 'N/A' as the value."
        )
        api_key_present = True # Set flag if configuration is successful
        logging.info("Gemini model configured successfully.")

except Exception as e:
    # Catch any exception during configuration (e.g., invalid key format recognized by genai)
    logging.error(f"Error configuring Gemini model: {e}")
    generator_model = None # Ensure model is None if configuration fails
    api_key_present = False


def review(paper):
    """
    Reviews a paper using a generative model, requesting JSON output.
    """
    if not api_key_present or generator_model is None:
        logging.error("Cannot perform review: Gemini model not available due to missing API key or configuration error.")
        # Return a placeholder that mimics the expected structure but indicates an error
        return json.dumps({
            "title_of_paper": "N/A",
            "author": "N/A",
            "year_of_publication": "N/A",
            "country_of_publication": "N/A",
            "research_objective": "Error: API key missing or invalid",
            "independent_variable_or_cause": "N/A",
            "dependent_variable_or_effect": "N/A",
            "estimation_techniques": "N/A",
            "theory": "N/A",
            "methods": "N/A",
            "findings": "N/A",
            "recommendations": "N/A",
            "research_gap": "N/A",
            "references": "N/A",
            "remarks": "Error: API key missing or invalid"
        })

    prompt = f"""Please review the following research paper and extract the requested information.
    Return the output STRICTLY as a JSON object.
    The JSON object should contain the following keys:
    'title_of_paper', 'author', 'year_of_publication', 'country_of_publication', 'research_objective',
    'independent_variable_or_cause', 'dependent_variable_or_effect', 'estimation_techniques', 'theory',
    'methods', 'findings', 'recommendations', 'research_gap', 'references', 'remarks'.

    If any of the requested information is not available in the paper, use 'N/A' for its value.
    Ensure all keys and string values in the JSON are enclosed in double quotes.

    Example JSON format:
    {{
        "title_of_paper": "Sample Title",
        "author": "Sample Author",
        "year_of_publication": "N/A",
        "country_of_publication": "N/A",
        "research_objective": "Sample objective here",
        "independent_variable_or_cause": "N/A",
        "dependent_variable_or_effect": "N/A",
        "estimation_techniques": "N/A",
        "theory": "N/A",
        "methods": "N/A",
        "findings": "N/A",
        "recommendations": "N/A",
        "research_gap": "N/A",
        "references": "N/A",
        "remarks": "N/A"
    }}

    The paper content is as follows:
    ---
    {paper}
    ---
    """

    try:
        response = generator_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating content from AI: {e}")
        return "" # Return empty string or specific error indicator