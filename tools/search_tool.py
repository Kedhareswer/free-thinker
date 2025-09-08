import requests
from dotenv import dotenv_values
import os
import urllib.parse
from bs4 import BeautifulSoup
import re


def search_duckduckgo(query):
    """Fallback search using DuckDuckGo instant answers and HTML scraping."""
    try:
        # Try DuckDuckGo instant answers API first
        instant_url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        response = requests.get(instant_url, params=params, timeout=10)
        if response.ok:
            data = response.json()
            if data.get('Abstract'):
                return f"DuckDuckGo Answer: {data['Abstract']}\nSource: {data.get('AbstractURL', 'DuckDuckGo')}"
            elif data.get('Answer'):
                return f"DuckDuckGo Answer: {data['Answer']}"
        
        # Fallback to HTML scraping if instant answer not available
        search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='result__body')[:3]  # Top 3 results
            
            formatted_output = "DuckDuckGo Search Results:\n"
            for result in results:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    formatted_output += f"• {title}: {snippet}\n"
            
            return formatted_output if len(results) > 0 else f"No DuckDuckGo results found for: {query}"
        
        return f"DuckDuckGo search failed for: {query}"
        
    except Exception as e:
        return f"DuckDuckGo search error: {str(e)}"


def search_bing_free(query):
    """Fallback search using Bing without API key (HTML scraping)."""
    try:
        search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('li', class_='b_algo')[:2]  # Top 2 results
            
            formatted_output = "Bing Search Results:\n"
            for result in results:
                title_elem = result.find('h2')
                snippet_elem = result.find('p')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    formatted_output += f"• {title}: {snippet}\n"
            
            return formatted_output if len(results) > 0 else f"No Bing results found for: {query}"
        
        return f"Bing search failed for: {query}"
        
    except Exception as e:
        return f"Bing search error: {str(e)}"


def search_tool(input_list):
    """
    Search the given query using multiple search engines.
    Tries Serper (Google) first, then falls back to DuckDuckGo and Bing.

    Parameters:
    input_list (list): A list containing only the query to search.

        Example format: ["longest river in the world"]

    Returns:
    (str): The formatted result of the search or an error message if something goes wrong.
    """
    try:
        query = input_list[0]
        CONFIG = dotenv_values("./config/.env")
        API_KEY = CONFIG.get("SERPER_API_KEY") or os.environ.get("SERPER_API_KEY")
        
        # Try Serper (Google) first if API key is available
        if API_KEY:
            try:
                params = {
                    'q': query,
                    'api_key': API_KEY
                }
                response = requests.get("https://google.serper.dev/search", params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if "organic" in data and len(data["organic"]) > 0:
                    formatted_output = "Google Search Results (via Serper):\n"
                    for result in data["organic"][:3]:  # Top 3 results
                        title = result.get("title", "No title")
                        snippet = result.get("snippet", "No snippet available")
                        formatted_output += f"• {title}: {snippet}\n"
                    return formatted_output
            except Exception as serper_error:
                print(f"Serper API failed: {serper_error}, falling back to free search...")
        
        # Fallback to free search engines
        print("Using free search engines (DuckDuckGo, Bing)...")
        
        # Try DuckDuckGo first
        ddg_result = search_duckduckgo(query)
        if "error" not in ddg_result.lower() and "failed" not in ddg_result.lower():
            return ddg_result
        
        # Try Bing as final fallback
        bing_result = search_bing_free(query)
        if "error" not in bing_result.lower() and "failed" not in bing_result.lower():
            return bing_result
        
        # If all searches fail
        return f"All search engines failed for query: {query}\n\nDDG: {ddg_result}\nBing: {bing_result}"

    except Exception as e:
        return f"Search tool error: {str(e)}"
