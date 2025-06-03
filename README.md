# Research Paper Review Assistant

This project is a Python-based research assistant that utilizes a generative AI model (Gemini 1.5 Flash) to automatically review research papers from PDF files. It extracts key information such as the paper's title, authors, publication year, research objectives, methodology, findings, and more, then saves this structured information into a CSV file.

## Features

*   **PDF Text Extraction:** Automatically extracts text content from PDF documents.
*   **AI-Powered Review:** Leverages the Gemini 1.5 Flash generative model to analyze the paper's content.
*   **Structured Data Extraction:** Identifies and extracts key information including:
    *   Title of paper
    *   Author(s)
    *   Year of publication
    *   Country of publication
    *   Research objective
    *   Independent variable or cause
    *   Dependent variable or effect
    *   Estimation techniques
    *   Theory
    *   Methods
    *   Findings
    *   Recommendation(s)
    *   Research gap
    *   References
    *   Remarks
*   **CSV Output:** Saves the extracted information in a structured CSV format for easy analysis and use.
*   **Error Handling:** Includes basic error handling for API interactions and PDF processing.

## Getting Started

### Prerequisites

*   Python 3.x (developed with Python 3.11)
*   The following Python libraries are required:
    *   `google-generativeai`
    *   `python-dotenv`
    *   `pdfplumber`
    *   `pandas`
*   A Google AI Studio API key for accessing the Gemini model. You can obtain one from [Google AI Studio](https://aistudio.google.com/).

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv research_assistant_env
    source research_assistant_env/bin/activate  # On Windows use: research_assistant_env\Scripts\activate
    ```

3.  **Install dependencies:**
    It's recommended to create a `requirements.txt` file with the following content:
    ```
    google-generativeai
    python-dotenv
    pdfplumber
    pandas
    ```
    Then, install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your Google AI Studio API Key:**
    *   Create a file named `.env` in the root directory of the project.
    *   Add your API key to the `.env` file as follows:
        ```
        google_ai_studio_key=YOUR_API_KEY
        ```
    Replace `YOUR_API_KEY` with your actual API key. The `.gitignore` file should already be configured to ignore `.env` files, but ensure it is to prevent committing your key.

## Usage

1.  **Prepare your PDF files:**
    *   Place the PDF research papers you want to review into a directory. For example, you can use the `data/papers/` directory or create a subdirectory within it (e.g., `data/papers/my_collection`).

2.  **Configure the input and output paths (Optional):**
    *   Open the `main.py` file.
    *   Modify the `pdf_input_directory` variable to point to the directory containing your PDF files.
        ```python
        pdf_input_directory = 'data/papers/your_pdf_folder'
        ```
    *   Modify the `output_csv_file` variable to specify the desired path and name for the output CSV file.
        ```python
        output_csv_file = 'data/response/your_review_output.csv'
        ```

3.  **Run the script:**
    Execute the `main.py` script from the root directory of the project:
    ```bash
    python main.py
    ```

4.  **Output:**
    *   The script will process each PDF file in the specified input directory.
    *   A CSV file will be generated at the specified `output_csv_file` path, containing the extracted information from the papers.
    *   The console will print "Done" when the process is complete. It will also list any files that failed to parse.

## Project Structure

```
.
├── .env                    # For API keys (gitignored)
├── .gitignore              # Specifies intentionally untracked files that Git should ignore
├── data/
│   ├── papers/             # Example directory for input PDF papers
│   └── response/           # Example directory for output CSV reviews
├── main.py                 # Main script to run the research review process
├── research_assistant/     # Virtual environment directory (if named this way)
├── src/
│   ├── reviewer.py         # Contains the logic for interacting with the AI model
│   ├── utils.py            # Utility functions for PDF processing and CSV saving
│   └── pg.py               # Currently an empty Python file
├── tests/
│   └── test_processing.py  # Example test file (actual tests might vary)
└── README.md               # This file
```

*   **`main.py`**: The entry point of the application. It orchestrates the PDF processing and review generation.
*   **`src/`**: Contains the core logic of the application.
    *   **`reviewer.py`**: Handles communication with the Google Generative AI model for paper review.
    *   **`utils.py`**: Provides helper functions for tasks like reading PDFs and saving CSV files.
    *   **`pg.py`**: Currently unused.
*   **`data/`**: Intended for storing input and output data.
    *   **`data/papers/`**: A suggested location to store input PDF files.
    *   **`data/response/`**: A suggested location where the output CSV files will be saved.
*   **`research_assistant/`**: Default directory for the Python virtual environment if created as per instructions.
*   **`tests/`**: Contains unit tests for the project.
*   **`.env`**: Stores environment variables, primarily the Google AI Studio API key. This file is not committed to version control.
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or want to report a bug, please feel free to open an issue or submit a pull request.

For major changes, please open an issue first to discuss what you would like to change.

## License

This project is currently unlicensed. You are free to add a license of your choice. Consider options like MIT, Apache 2.0, or GPL, depending on your preferences.
