import google.generativeai as genai
import os
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPIError

# Load environment variables from .env file
load_dotenv()

# Configure the generative AI model
api_key = os.getenv('google_ai_studio_key')
genai.configure(api_key=api_key)

generator_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are an experienced doctoral research assistant. I want you to read a paper and get the "
                       "following information: title of paper; author; year of publication; country of publication; "
                       "research objective; independent variable or cause; dependent variable or effect; estimation "
                       "techniques; theory; methods; findings, recommendation(s); research gap; references; and "
                       "remarks where necessary. Your response should be in the form "
                       "{title of paper:'...', author:'...', year of publication:'...', country of "
                       "publication:'...', research objective:'...', independent variable or cause:'...', "
                       "dependent variable or effect:'...', estimation techniques:'...', theory:'...', methods:'...', "
                       "findings:'...', recommendation(s):'...', research gap:'...', references:'...', remarks:'...'}"
)


def review(paper):
    """
    review paper using a generative model.
    """
    prompt = f"""The researcher wants you to help review a paper and return a Python dictionary containing the 
    following: title of paper; author; year of publication; country of publication; research objective; independent 
    variable or cause; dependent variable or effect; estimation techniques; theory; methods; findings, 
    recommendation(s); research gap; references; and remarks where necessary. If any of the requested information is 
    not available, fill it as 'N/A'. 

    Return only the Python dictionary and ensure it follows this exact format with all key-value pairs enclosed 
    in single quotation marks, as shown below:

    {{
        'title of paper': 'Sample Title',
        'author': 'Sample Author',
        'year of publication': 'N/A',
        'country of publication': 'N/A',
        'research objective': 'Sample objective here',
        ...
    }}

    The paper is contained here: {paper}
    """

    try:
        response = generator_model.generate_content(prompt)
        return response.text
    except GoogleAPIError as e:
        print(f"API Error during review: {e}")
        return "{'error': 'API call failed during review'}"
    except Exception as e:
        print(f"An unexpected error occurred during review: {e}")
        return "{'error': 'API call failed during review'}"
