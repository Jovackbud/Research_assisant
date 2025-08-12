import os
from dotenv import load_dotenv
import logging
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables from .env file
load_dotenv()

# --- Global variable to hold the model ---
generator_model = None
api_key_present = False # Flag to track if API key was found

try:
    api_key = os.getenv('google_ai_studio_key')
    if not api_key:
        logging.error("Google AI API key 'google_ai_studio_key' not found in .env file. Gemini model will not be available.")
    else:
        generator_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key
        )
        api_key_present = True
        logging.info("LangChain Gemini model configured successfully.")
except Exception as e:
    logging.error(f"Error configuring LangChain Gemini model: {e}")
    generator_model = None
    api_key_present = False


def review(paper):
    """
    Reviews a paper using a generative model, requesting JSON output.
    """
    if not api_key_present or generator_model is None:
        logging.error("Cannot perform review: Gemini model not available due to missing API key or configuration error.")
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

    system_instruction = (
        "You are an experienced doctoral research assistant. Your task is to extract specific information from research papers and provide it in a structured JSON format. "
        "Ensure all keys are in snake_case. If any information is unavailable, use 'N/A' as the value."
    )
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
        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=prompt)
        ]
        response = generator_model.invoke(messages)
        # LangChain returns a Message object; get the content
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logging.error(f"Error generating content from AI: {e}")
        return ""