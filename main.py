from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import requests
import json

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--window-size=1920,1080")  # Set window size
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation flags
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Disable automation flags
chrome_options.add_experimental_option("useAutomationExtension", False)  # Disable automation flags
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Set a real user-agent

# Function to scrape Google search results for French websites
def scrape_google_search(product_name):

    # Initialize Chrome WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open Google France
        driver.get("https://www.google.fr")

        # Add a random delay to mimic human behavior
        time.sleep(random.uniform(2, 5))

        # Find the search box and enter the product name
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.RETURN)

        # Wait for the page to load
        time.sleep(random.uniform(3, 6))

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract the first 5 search results
        results = []
        for result in soup.find_all("div", class_="tF2Cxc")[:5]:  # Limit to first 5 results
            title = result.find("h3").text if result.find("h3") else "No Title"
            link = result.find("a")["href"] if result.find("a") else "No Link"
            results.append({"title": title, "link": link})

        return results

    finally:
        # Close the browser
        driver.quit()

# Function to scrape text from a webpage using Selenium
def scrape_webpage_text(url):

    # Initialize Chrome WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open the webpage
        driver.get(url)

        # Add a random delay to mimic human behavior
        time.sleep(random.uniform(3, 6))

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return soup.get_text()

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

    finally:
        # Close the browser
        driver.quit()

# Function to query Ollama's local LLM
def query_ollama(product_name, scraped_text, url):
    # Ollama API endpoint
    API_URL = "http://localhost:11434/api/generate"

    # Prepare the prompt
    prompt = f"""
    You are an intelligent assistant. Below is the scraped text from a webpage. 
    The product being searched for is: {product_name}.
    Extract the following information from the text:
    1. Extracted Product Name (the exact name of the product as mentioned on the webpage)
    2. Store Name (the name of the store or website)
    3. Original price (in €)
    4. Discounted price (if available, in €)
    5. Stock availability (In Stock or Out of Stock)

    **IMPORTANT**: Respond ONLY in the following JSON format. Do not include any additional text or explanations.
    {{
        "extracted_product_name": "exact product name (or '-' if not found)",
        "store_name": "store or website name (or '-' if not found)",
        "original_price": "original price (or '-' if not found)",
        "discounted_price": "discounted price (or '-' if not found)",
        "stock_availability": "In Stock or Out of Stock (or '-' if not found)"
    }}

    **Rules**:
    1. Respond ONLY in the specified JSON format. Do not include any additional text, explanations, or symbols.
    2. If the price or stock availability is not found, use "-".
    3. If the product name or store name is not found, use "-".
    4. Do not deviate from the JSON format under any circumstances.

    Scraped Text:
    {scraped_text[:5000]}  # Limit to first 5000 characters to avoid overloading the LLM
    """

    # Query Ollama
    payload = {
        "model": "llama2", 
        "prompt": prompt,
        "stream": False  # Set to False to get a single response
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            llm_response = response.json()["response"]
            print(f"LLM Response: {llm_response}")  # Debugging

            # Parse the LLM response into a dictionary
            try:
                data = json.loads(llm_response)  # Convert JSON string to dictionary
                data["url"] = url  # Add the URL to the data
                return data
            except json.JSONDecodeError:
                print("LLM did not return valid JSON. Using fallback values.")
                return {
                    "extracted_product_name": "-",
                    "store_name": "-",
                    "original_price": "-",
                    "discounted_price": "-",
                    "stock_availability": "-",
                    "url": url
                }
        else:
            print(f"Error querying Ollama: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None

# Function to update the CSV file with product data
def update_csv(product_name, data, filename="product_tracking.csv"):
    try:
        # Load existing CSV file or create a new one
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Product Name", "Extracted Product Name", "Store Name", "URL", 
            "Original Price", "Discounted Price", "Stock Availability"
        ])

    # Add new results to the DataFrame
    new_row = {
        "Product Name": product_name,
        "Extracted Product Name": data.get("extracted_product_name", "-"),
        "Store Name": data.get("store_name", "-"),
        "URL": data.get("url", "No URL"),
        "Original Price": data.get("original_price", "-"),
        "Discounted Price": data.get("discounted_price", "-"),
        "Stock Availability": data.get("stock_availability", "-")
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Filter rows: Remove rows with missing prices or stock availability
    df = df[
        (df["Original Price"] != "-") & 
        (df["Stock Availability"] != "-")
    ]

    # Save the updated DataFrame to CSV
    df.to_csv(filename, index=False)

# Main function
if __name__ == "__main__":
    # List of products to track
    products = ["Levi`s jean orignal 510", "Lacoste Monogram Jacquard Hoodie Size 34 Green/Green Khaki – Lacoste", "Men's Club Harrington Corduroy Jacket Black/White", "Lacoste Legging Sport stretch Ultra Dry printed Size XS Purple – Lacoste", "Lacoste T-shirt Sport Ultra Dry logo XXL Size XS Black/Khaki green – Lacoste"]

    for product in products:
        print(f"Searching for: {product}")
        search_results = scrape_google_search(product)

        for result in search_results[:5]:  # Process only the first 5 results
            print(f"Scraping: {result['link']}")
            scraped_text = scrape_webpage_text(result["link"])

            if scraped_text:
                print("Querying Ollama...")
                data = query_ollama(product, scraped_text, result["link"])
                if data:
                    print(f"LLM Response: {data}")
                    update_csv(product, data)

    print("Product tracking completed. Results saved to 'product_tracking.csv'.")