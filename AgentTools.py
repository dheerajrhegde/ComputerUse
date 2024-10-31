from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
import pandas as pd
import webbrowser
import subprocess
import pytesseract
from PIL import Image
import openai
import time
import os
import requests
from bs4 import BeautifulSoup
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from selenium import webdriver
from selenium.webdriver.common.by import By
from langchain_openai import ChatOpenAI
from selenium.webdriver.chrome.options import Options

pytesseract.pytesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.4.1_1/bin/tesseract'

class FileName(BaseModel):
    file_path: str = Field(description="Full path of the excel file to open and get address")

@tool(args_schema=FileName)
def get_excel_data(file_path):
    """
    Open the excel specified by the path and get the data from the excel.
    Return data as a dataframe
    :param file_path:
    :return:
    """
    print("calling get_excel_data with ", file_path)
    try:
        # Launch the Excel application to open the file (optional step)
        subprocess.run(['open', '-a', 'Microsoft Excel', file_path])
        print(f"Excel file '{file_path}' opened successfully.")

        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(file_path)
        print("Excel data copied into DataFrame successfully.")
        return df
    except Exception as e:
        print(f"Failed to open the Excel file: {e}")
        return None


class SearchQuery(BaseModel):
    query: str = Field(description="Search query to send to google.com")

@tool(args_schema=SearchQuery)
def search_google(query):
    """
    Search on google.com using the query provided
    :param query:
    :return:
    """
    print("calling search_google with ", query)
    json_parser = JsonOutputParser()
    # Step 1: Open Google in the default browser
    query_encoded = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query_encoded}"
    webbrowser.open(url)
    print(f"Searching for '{query}' in the default browser.")

    # Step 2: Wait a few seconds to allow the browser to load
    time.sleep(5)  # Adjust the time if needed to ensure the page has loaded

    # Step 3: Take a screenshot using macOS built-in tool and save on disk
    screenshot_path = "screenshot.png"
    try:
        subprocess.run(['screencapture', '-x', screenshot_path])
        image = Image.open(screenshot_path)
        print("Screenshot taken and saved on disk.")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return

    # Step 4: Use Tesseract to extract text from the screenshot
    try:
        extracted_text = pytesseract.image_to_string(image)
        print("Extracted Text from Screenshot:")
        print(extracted_text)
    except Exception as e:
        print(f"Failed to extract text from screenshot: {e}")
        return

    # Step 5: Send the extracted text to OpenAI for analysis
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an helpful assistant."},
                {"role": "user",
                 "content": f"Analyze the following text extracted from a Google search result: {extracted_text} and answer this question: {query}"}
            ]
        )
        print("OpenAI Response:")
        print(response.choices[0].message.content)
        analyzed_text = response.choices[0].message.content
    except Exception as e:
        print(f"Failed to send extracted text to OpenAI: {e}")
        return
    finally:
        # Delete the screenshot file
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            print(f"Screenshot file '{screenshot_path}' deleted.")

    return analyzed_text

class Analyzedtext(BaseModel):
    analyzed_text: str = Field(description="text about the company based o user prompt")

@tool(args_schema=Analyzedtext)
def enter_data(analyzed_text):
    """
    Enter the data into the data entry portal
    :param analyzed_text:
    :return:
    """
    print("calling enter_data with ", analyzed_text)
    # Step 6: Open localhost:8000 in a new browser window and determine form fields
    try:
        # Fetch the HTML content of the localhost page
        response = requests.get("http://localhost:8000")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all form fields and determine where to input the data
        form_fields = soup.find_all('input') + soup.find_all('textarea')
        if not form_fields:
            print("No form fields found on the page.")
            return

        # Prepare form field details for LangChain analysis
        form_field_details = [
            {
                "name": field.get('name'),
                "id": field.get('id'),
                "type": field.get('type'),
                "placeholder": field.get('placeholder')
            } for field in form_fields
        ]

        print(form_field_details)
        json_parser = JsonOutputParser()

        # Use LangChain to analyze where to put the data
        prompt = PromptTemplate(
            input_variables=["fields", "text"],
            template="""
                You are an AI that helps to determine which text goes into which form fields. Here is the list of form fields:
                {fields}
                Here is the text to be entered: {text}
                Please return a JSON object that maps form field IDs or names to the text that should be entered. {format_instructions}
                """,
            partial_variables={"format_instructions": json_parser.get_format_instructions()},
        )

        model = ChatOpenAI(api_key=os.environ["OPENAI_API_KEY"], temperature=0)
        chain = prompt | model | json_parser
        parsed_response = chain.invoke({"fields": form_field_details, "text": analyzed_text})
        print("parsed_response", parsed_response)

        # Step 7: Open the page in a browser and enter data using Selenium
        # service = Service('/path/to/chromedriver')  # Update with the correct path to ChromeDriver
        options = Options()
        options.add_experimental_option("detach", True)
        #driver = webdriver.Safari(options=options)
        driver = webdriver.Safari()
        driver.get("http://localhost:8000")
        print("Opened localhost:8000 in a new browser window.")

        # Wait for the page to load
        time.sleep(5)

        # Use Selenium to enter the data based on LangChain's output
        for field_id, field_data in parsed_response.items():
            try:
                # Find the form field using its ID or name
                if field_id:
                    field_element = driver.find_element(By.ID, field_id) if driver.find_elements(By.ID,
                                                                                                 field_id) else driver.find_element(
                        By.NAME, field_id)
                    field_element.clear()
                    field_element.send_keys(field_data)
                    print(f"Entered data into field '{field_id}': {field_data}")
            except Exception as e:
                print(f"Failed to enter data into field '{field_id}': {e}")

    except Exception as e:
        print(f"Failed to interact with localhost form: {e}")

    time.sleep(5)
