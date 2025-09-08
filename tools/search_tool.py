import requests
from dotenv import dotenv_values
import os


def search_tool(input_list):
    """
    Search the given query on google.

    Parameters:
    input_list (list): A list containing only the query to search on google.

        Example format: ["longest river in the world"]

    Returns:
    (str): The formatted result of the search or an error message if something goes wrong.
    """
    try:
        query = input_list[0]
        CONFIG = dotenv_values("./config/.env")
        API_KEY = CONFIG.get("SERPER_API_KEY") or os.environ.get("SERPER_API_KEY")
        
        if not API_KEY:
            return "\nError: SERPER_API_KEY not found. Please provide it in the UI or config/.env"
        
        params = {
            'q': query,
            'api_key': API_KEY
        }
        response = requests.get(
            "https://google.serper.dev/search", params=params)
        response.raise_for_status()
        data = response.json()
        
        if "organic" not in data:
            return f"\nNo search results found for: {query}"
        
        formatted_output = ""
        for result in data["organic"]:
            snippet = result.get("snippet", "No snippet available")
            formatted_output = formatted_output + snippet + "\n"
        return formatted_output

    except Exception as e:
        return f"\nError occurred: {str(e)}"
