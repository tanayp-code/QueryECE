import requests
from bs4 import BeautifulSoup
import json
import os

BASE_URL = "https://iitr.ac.in/Departments/Electronics%20and%20Communication%20Engineering%20Department/Home.html"

def scrape_ece_home():
    print(f"Fetching data from {BASE_URL}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    scraped_data = {
        "department": "Electronics and Communication Engineering",
        "institution": "IIT Roorkee",
        "announcements": [],
        "links": []
    }

    # Extract text content from news and announcements list items
    items = soup.find_all(['li', 'p', 'a']) 
    
    for item in items:
        text = item.get_text(strip=True)
        if len(text) > 30 and text not in scraped_data["announcements"]:
            scraped_data["announcements"].append(text)
            
        href = item.get('href')
        if href and href.startswith('http'):
            scraped_data["links"].append({"text": text, "url": href})

    # Save to data directory at root level
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
    os.makedirs(data_dir, exist_ok=True)
    
    output_path = os.path.join(data_dir, "static_content.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully scraped content. Total announcements extracted: {len(scraped_data['announcements'])}")
    print(f"Data saved to: {output_path}")

if __name__ == "__main__":
    scrape_ece_home()