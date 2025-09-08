from dotenv import dotenv_values
from datetime import datetime
import requests
import os
import urllib.parse
from bs4 import BeautifulSoup
import re


def search_weather_info(city):
    """Get weather information using free web search."""
    try:
        # Try multiple search queries for weather
        queries = [
            f"weather {city} today temperature",
            f"current weather {city}",
            f"{city} weather forecast today"
        ]
        
        for query in queries:
            # Try DuckDuckGo first
            weather_info = search_duckduckgo_weather(query, city)
            if weather_info and "error" not in weather_info.lower():
                return weather_info
            
            # Try Bing as fallback
            weather_info = search_bing_weather(query, city)
            if weather_info and "error" not in weather_info.lower():
                return weather_info
        
        return f"Unable to find weather information for {city}"
        
    except Exception as e:
        return f"Weather search error: {str(e)}"


def search_duckduckgo_weather(query, city):
    """Search weather using DuckDuckGo."""
    try:
        # Try DuckDuckGo instant answers first
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
            if data.get('Answer'):
                return f"Weather in {city}:\n{data['Answer']}\n(Source: DuckDuckGo)"
            elif data.get('Abstract'):
                return f"Weather in {city}:\n{data['Abstract']}\n(Source: DuckDuckGo)"
        
        # Fallback to HTML scraping
        search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='result__body')[:2]
            
            weather_info = f"Weather information for {city}:\n"
            for result in results:
                snippet_elem = result.find('a', class_='result__snippet')
                if snippet_elem:
                    snippet = snippet_elem.get_text(strip=True)
                    if any(word in snippet.lower() for word in ['temperature', 'weather', '°', 'celsius', 'fahrenheit']):
                        weather_info += f"• {snippet}\n"
            
            return weather_info if len(weather_info) > len(f"Weather information for {city}:\n") else None
            
    except Exception as e:
        return None


def search_bing_weather(query, city):
    """Search weather using Bing."""
    try:
        search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for weather-specific content
            weather_cards = soup.find_all('div', class_=['b_algo', 'weather'])
            
            weather_info = f"Weather information for {city}:\n"
            for card in weather_cards[:2]:
                text = card.get_text(strip=True)
                if any(word in text.lower() for word in ['temperature', 'weather', '°', 'celsius', 'fahrenheit']):
                    # Extract relevant weather information
                    lines = text.split('\n')
                    for line in lines[:3]:  # First few lines usually contain weather data
                        if line.strip() and any(word in line.lower() for word in ['°', 'temp', 'weather']):
                            weather_info += f"• {line.strip()}\n"
            
            return weather_info if len(weather_info) > len(f"Weather information for {city}:\n") else None
            
    except Exception as e:
        return None


def extract_weather_from_general_search(city):
    """Extract weather info from general web search results."""
    try:
        # Search for weather on popular weather sites
        weather_sites_queries = [
            f"site:weather.com {city} weather",
            f"site:accuweather.com {city} current weather",
            f"site:weather.gov {city} weather"
        ]
        
        for query in weather_sites_queries:
            try:
                search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.ok:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.find_all('div', class_='result__body')[:1]
                    
                    for result in results:
                        snippet_elem = result.find('a', class_='result__snippet')
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                            if len(snippet) > 50:  # Ensure substantial content
                                return f"Weather in {city}:\n{snippet}\n(Source: Weather website)"
            except:
                continue
                
        return None
        
    except Exception as e:
        return None


def weather_forecaster(input_list):
    """
    Get current weather on specified location using free web search.
    No API keys required - uses DuckDuckGo and Bing search.

    Parameters:
    input_list (list): A list containing the location from where you want to check the weather.

        Example format: ["London"]

    Returns:
    (str): The formatted weather or an error message if something goes wrong.
    """
    try:
        if not input_list or not isinstance(input_list, list) or not input_list[0]:
            return "Error: Please provide a valid city name."

        city = input_list[0].strip()
        
        print(f"Searching for weather information for {city} using free sources...")
        
        # Try different search approaches
        weather_info = search_weather_info(city)
        
        if not weather_info or "unable to find" in weather_info.lower():
            # Try general search as final fallback
            weather_info = extract_weather_from_general_search(city)
            
        if not weather_info:
            return f"Unable to retrieve weather information for {city}. Please try again or check the city name."
            
        # Add timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        weather_info += f"\nRetrieved at: {current_time}"
        weather_info += "\nNote: Weather data obtained from free web sources. For most accurate information, check official weather services."
        
        return weather_info

    except Exception as e:
        return f"Weather tool error: {str(e)}"
