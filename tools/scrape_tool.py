from bs4 import BeautifulSoup
import requests
import urllib.parse
import re
from datetime import datetime


def search_for_page_info(url):
    """Get additional context about a webpage using search engines."""
    try:
        # Extract domain and keywords from URL for search
        domain = urllib.parse.urlparse(url).netloc
        path_parts = urllib.parse.urlparse(url).path.split('/')
        
        # Create search queries to get more context
        search_queries = [
            f"site:{domain} {' '.join(path_parts[-2:])}" if len(path_parts) > 2 else f"site:{domain}",
            f"{domain} content information",
            f"about {domain}"
        ]
        
        context_info = ""
        
        for query in search_queries[:1]:  # Try just one query to avoid spam
            try:
                # Use DuckDuckGo search for context
                search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(search_url, headers=headers, timeout=8)
                
                if response.ok:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.find_all('div', class_='result__body')[:2]
                    
                    for result in results:
                        snippet_elem = result.find('a', class_='result__snippet')
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                            if len(snippet) > 30:
                                context_info += f"Context: {snippet}\n"
                                break
                    break
            except:
                continue
                
        return context_info
        
    except Exception as e:
        return f"Context search error: {str(e)}\n"


def enhanced_content_extraction(soup, url):
    """Enhanced content extraction with multiple strategies."""
    try:
        content_sections = []
        
        # Strategy 1: Look for main content areas
        main_content = soup.find(['main', 'article', 'div'], class_=re.compile(r'content|main|article|post', re.I))
        if main_content:
            paragraphs = main_content.find_all(['p', 'div'], class_=lambda x: x != 'nav' and x != 'sidebar')
            for p in paragraphs[:10]:  # Limit to avoid too much content
                text = p.get_text(strip=True)
                if len(text) > 50:  # Only substantial content
                    content_sections.append(text)
        
        # Strategy 2: Get all paragraphs if main content not found
        if not content_sections:
            paragraphs = soup.find_all('p')
            for p in paragraphs[:15]:  # Limit paragraphs
                text = p.get_text(strip=True)
                if len(text) > 30:
                    content_sections.append(text)
        
        # Strategy 3: Get headings for structure
        headings = soup.find_all(['h1', 'h2', 'h3'])
        heading_info = ""
        for h in headings[:5]:  # Limit headings
            heading_text = h.get_text(strip=True)
            if len(heading_text) > 5:
                heading_info += f"• {heading_text}\n"
        
        # Combine content
        extracted_content = ""
        if heading_info:
            extracted_content += f"Key Topics:\n{heading_info}\n"
        
        if content_sections:
            extracted_content += "Content:\n"
            for section in content_sections[:8]:  # Limit sections
                extracted_content += f"{section}\n\n"
        
        return extracted_content if extracted_content else "No substantial content found."
        
    except Exception as e:
        return f"Content extraction error: {str(e)}"


def get_page_metadata(soup, url):
    """Extract useful metadata from the page."""
    try:
        metadata = ""
        
        # Title
        title = soup.find('title')
        if title:
            metadata += f"Title: {title.get_text(strip=True)}\n"
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata += f"Description: {meta_desc.get('content')}\n"
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            metadata += f"Keywords: {meta_keywords.get('content')}\n"
        
        return metadata + "\n" if metadata else ""
        
    except Exception as e:
        return f"Metadata extraction error: {str(e)}\n"


def scrape_tool(input_list):
    """
    Enhanced web scraper that extracts comprehensive information from webpages.
    Uses advanced content extraction, metadata analysis, and search context.
    No API keys required.

    Parameters:
    input_list (list): A list containing only the url of the webpage to scrape.

        Example format: ["https://en.wikipedia.org/wiki/Estelle,_Louisiana"]

    Returns:
    (str): Enhanced formatted result with content, metadata, and context.
    """
    try:
        if not input_list or not isinstance(input_list, list) or not input_list[0]:
            return "Error: Please provide a valid URL."
            
        url = input_list[0].strip()
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        print(f"Enhanced scraping of: {url}")
        
        # Get the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Build comprehensive output
        output = f"=== Enhanced Web Scraping Results ===\n"
        output += f"URL: {url}\n"
        output += f"Status: Successfully accessed\n"
        output += f"Scraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Get metadata
        metadata = get_page_metadata(soup, url)
        if metadata:
            output += f"=== Page Information ===\n{metadata}"
        
        # Get enhanced content
        content = enhanced_content_extraction(soup, url)
        output += f"=== Main Content ===\n{content}\n"
        
        # Get search context (optional, may take extra time)
        try:
            context = search_for_page_info(url)
            if context and len(context.strip()) > 10:
                output += f"=== Additional Context ===\n{context}\n"
        except:
            pass  # Don't fail if context search fails
        
        output += "=== End of Scraping Results ===\n"
        output += "Note: Content extracted using enhanced web scraping. For real-time data, visit the original URL."
        
        return output

    except requests.exceptions.RequestException as e:
        return f"Network error while accessing {url}: {str(e)}"
    except Exception as e:
        return f"Web scraping error: {str(e)}"
