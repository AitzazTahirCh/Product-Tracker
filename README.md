# Product-Tracker

This project is designed to track the availability, original price, and discounted price of products across multiple French brands. It scrapes product data from Google search results, processes the data using a local Large Language Model (LLM) via Ollama, and saves the results to a CSV file.

While this task can be accomplished in multiple ways, the simplest approach would be to use an API like SerpApi for fetching search results. However, given the constraints of this test, I have implemented a solution that scrapes search results directly and uses an LLM to extract the required data. This approach is necessary because every e-commerce website has a unique structure for displaying product information. Using an LLM allows for a more generalized and flexible solution, as it can adapt to varying website structures and extract information from it without requiring custom scraping logic for each site.

For this project, I used Ollama with a small local Llama LLM. While this works well for the current scope, using a larger and more powerful LLM would improve efficiency and accuracy, especially when dealing with complex or diverse website structures. Alternatively, custom scraping scripts could be written for specific websites, but this approach would not be as scalable or adaptable to different e-commerce platforms.


## Features
- **Product Search**: Searches for products on Google France and extracts relevant links.
- **Web Scraping**: Scrapes product details (price, stock availability) from the extracted links.
- **LLM Integration**: Uses a local LLM (via Ollama) to extract structured data from scraped text.
- **CSV Output**: Saves the extracted data to a CSV file (`product_tracking.csv`).
- **Scalability**: Designed to handle large-scale product tracking efficiently.

## Requirements
- Python 3.8 or higher
- ChromeDriver (for Selenium)
- Ollama (for local LLM)

## Running the script

- Install the required dependencies: 'pip install -r requirements.txt'
- Install Ollama and download a model (e.g., Llama 2) or use some api i.e openAI one
- Run the script 'python main.py'
The results will be saved to product_tracking.csv

## Deployment for Daily Execution
To run this script daily, you can deploy it to a cloud service like Google Cloud Run or Azure Functions.
Set up a Timer Trigger to run the function daily.

## Output
The script generates a CSV file (product_tracking.csv) with the following columns:

Product Name: The name of the product being tracked.

Extracted Product Name: The exact name of the product as mentioned on the webpage.

Store Name: The name of the store or website.

URL: The URL of the product page.

Original Price: The original price of the product.

Discounted Price: The discounted price of the produc, if available.

Stock Availability: The stock status (In Stock or Out of Stock).

