# Computer Use

Few weeks back Anthripic launched Computer Use capability in Claude 3.5 Sonnet and Haiku. With this, users can have LLM developers can direct Claude to use computers the way people do.  https://www.anthropic.com/news/3-5-models-and-computer-use. 

Sam Ringer from Antropic developer relations demonstrated the feature at https://www.youtube.com/watch?v=ODaHJzOyVCQ where he checks if data is available in a spreadsheet. If not available, searches for it on google and enters the data into a web form. 

For me this is a good example of how, in the future, Agents that we build will be part of the core LLM. As explained by Harrison Chase here https://youtu.be/S9cz94jgZ4c?t=1417. 

Now, ff you don't have access to Claude, you can implement the same with your LLM of choice, provided it has function calling capability. I have demonstrated this method in my medium post. Here I ask OpenAI based Agentic application to find corporate headquarters for a company. It:
- Look for the address in an excel. Opens the excel on the desktop
- If found, open a HTML form and submits the information on that form. In doing so understand the form and the data available to match the data to the form fields. 
- If not found, open a browser to do a google search
- Gets the data from the browser, launches the HTMNL form and submits the data.

Demo can be found at https://youtu.be/tSfgqjUmA9E
Code at https://github.com/dheerajrhegde/ComputerUse

## Features
- **Excel Data Extraction**: Read data from Excel files using Pandas.
- **Automated Google Search**: Search for information on Google and analyze results using OpenAI.
- **Web Form Interaction**: Automatically enter extracted data into a web form using Selenium.
- **State Machine Agent**: The workflow is managed using a state machine (`StateGraph`), making the agent capable of interacting with various tools intelligently.

## Tools and Technologies Used
- **LangChain**: Used to create a state machine (`StateGraph`) for managing the workflow of the agent.
- **OpenAI GPT-4**: Employed for natural language processing, extracting meaning, and analyzing data from Google search results.
- **Pandas**: Utilized for reading data from Excel files.
- **Tesseract OCR**: Extracts text from screenshots for further analysis.
- **Selenium**: Automates interaction with web forms.
- **BeautifulSoup**: Parses HTML content for identifying form fields.
- **Pydantic**: Used for defining schemas for tool arguments.

## Project Structure
- **AgentTools.py**: Contains the definition of the tools used by the agent, including functions for getting Excel data, searching Google, and entering data into a form.
- **Agent Class**: Defines the agent, including its state machine and logic for interacting with tools and models.
- **Streamlit Interface**: Provides a simple user interface for interacting with the agent, where users can enter a prompt to trigger automation.

## How It Works
1. **Excel Data Extraction** (`get_excel_data`): The agent opens and reads the specified Excel file, extracting data into a Pandas DataFrame.
2. **Google Search** (`search_google`): If the requested data isn't available in the Excel file, the agent performs a Google search using Selenium to fetch relevant information.
3. **Web Form Interaction** (`enter_data`): Once the required data is obtained, the agent opens a web form on `localhost:8000`, analyzes the form fields, and uses Selenium to enter the information accordingly.
4. **State Machine Flow**: The state machine (`StateGraph`) determines the sequence of operations for the agent, starting with invoking the language model and transitioning to specific tools as needed.

## Installation
To set up the project locally, follow these steps:

1. **Clone the Repository**:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   Install the required packages listed in `requirements.txt`:
   ```sh
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   - Set up environment variables for OpenAI:
     ```sh
     export OPENAI_API_KEY="your_openai_api_key"
     ```
   - Ensure Tesseract OCR is installed and set the correct path in the code:
     ```python
     pytesseract.pytesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.4.1_1/bin/tesseract'
     ```
   - Install [ChromeDriver](https://chromedriver.chromium.org/downloads) for Selenium or use Safari if you prefer.

## Running the Project
1. **Streamlit Interface**:
   Launch the Streamlit interface to interact with the agent:
   ```sh
   streamlit run app.py
   ```

2. **Submit a Task**:
   Enter a task prompt (e.g., "Find the headquarter address for Infosys and enter it into the data entry portal.") and click "Submit".

## Dependencies
- **Python 3.8+**
- **Pandas** for Excel handling
- **Tesseract OCR** for text extraction
- **Selenium** for browser automation
- **LangChain** for creating the agent and workflow management
- **OpenAI** API for text analysis
- **BeautifulSoup** for parsing HTML content

## Troubleshooting
- **Excel File Not Found**: Ensure the Excel file path is correct.
- **Tesseract Not Found**: Update the `pytesseract.pytesseract_cmd` with the correct path to the Tesseract executable.
- **Selenium Issues**: Ensure you have the correct browser driver installed (e.g., ChromeDriver, SafariDriver).

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

## Contributing
Contributions are welcome! If you'd like to contribute, please open an issue or submit a pull request.

## Contact
For any questions or issues, please contact the author at [your-email@example.com].

