from src.utils import extract_text_from_pdf
from unittest.mock import patch, MagicMock
import pdfplumber # Required for type hinting if used by mock
import re
import ast
import pytest # For pytest.raises

def test_extract_text_from_pdf_normal_case(mocker):
    # Mock the behavior of pdfplumber.open
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Text from page 1. "
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Text from page 2."
    
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page1, mock_page2]
    
    # pdfplumber.open returns a context manager, so mock its __enter__ method
    mock_open = mocker.patch('pdfplumber.open', autospec=True)
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_text_from_pdf("dummy/path.pdf")
    assert result == "Text from page 1. Text from page 2."
    mock_open.assert_called_once_with("dummy/path.pdf")

def test_extract_text_from_pdf_handles_exception(mocker):
    mock_open = mocker.patch('pdfplumber.open', autospec=True)
    mock_open.side_effect = Exception("PDF processing error")

    # Optional: If you want to check print output, you can mock builtins.print
    # mock_print = mocker.patch('builtins.print')

    result = extract_text_from_pdf("dummy/path.pdf")
    assert result == ""
    # mock_print.assert_called_with(expected_error_message) # If checking print

# Test for dictionary parsing logic similar to main.py
def test_api_response_parsing_valid():
    api_response = "Some text before ... {'key': 'value', 'number': 123} ... some text after"
    expected_dict = {'key': 'value', 'number': 123}
    
    match = re.search(r"\{.*\}", api_response, re.DOTALL)
    assert match is not None
    dictionary_content = match.group(0)
    result_dict = ast.literal_eval(dictionary_content)
    
    assert result_dict == expected_dict

def test_api_response_parsing_invalid():
    # Malformed dict string that re.search will find, but ast.literal_eval will fail on.
    api_response = "Some text before ... {'key': 'value', 'number': unquoted_string } ... some text after" 
    
    match = re.search(r"\{.*\}", api_response, re.DOTALL)
    assert match is not None
    dictionary_content = match.group(0)
    
    with pytest.raises((SyntaxError, ValueError)):
        ast.literal_eval(dictionary_content)
