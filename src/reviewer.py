import google.generativeai as genai
import os
from dotenv import load_dotenv

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
    prompt = f""" The researcher wants you to help review a paper and return a dictionary containing the following: 
    title of paper; author; year of publication; country of publication; research objective; independent variable or 
    cause; dependent variable or effect; estimation techniques; theory; methods; findings, recommendation(s); 
    research gap; references; and remarks where necessary. If any of the requested information are not available, 
    fill it as N/A. The paper is contained here: {paper}
    """
    response = generator_model.generate_content(prompt)
    return response.text
