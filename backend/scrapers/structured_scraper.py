from playwright.sync_api import sync_playwright
import json
import os
import re

FACULTY_LIST_URL = "https://iitr.ac.in/Departments/Electronics%20and%20Communication%20Engineering%20Department/People/Faculty/FACULTY%20MEMBERS.html"
BASE_DOMAIN = "https://iitr.ac.in"

def deep_scrape_faculty():
    print("Starting Deep Faculty Crawler...")
    
    detailed_faculty_list = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"1. Fetching main directory index: {FACULTY_LIST_URL}")
        page.goto(FACULTY_LIST_URL, wait_until="networkidle")
        page.wait_for_timeout(2000)
        
        # Extract all profile links and basic info from the main page cards/rows
        # We look for anchor tags that point to individual profile pages (usually numeric IDs like 100923.html)
        profile_links = page.locator("a[href*='People/Faculty']")
        
        links_to_visit = set()
        count = profile_links.count()
        
        for i in range(count):
            element = profile_links.nth(i)
            href = element.get_attribute("href")
            if href and ("html" in href or "php" in href) and "FACULTY" not in href:
                full_url = href if href.startswith("http") else BASE_DOMAIN + href.replace("../", "")
                links_to_visit.add(full_url)
                
        print(f"Found {len(links_to_visit)} individual profile links to deep-crawl.")
        
        # Stage 2: Loop through each individual profile page
        for idx, profile_url in enumerate(links_to_visit):
            print(f"[{idx+1}/{len(links_to_visit)}] Crawling subpage: {profile_url}")
            try:
                page.goto(profile_url, wait_until="networkidle", timeout=10000)
                
                # Extract all text from the subpage
                body_text = page.locator("body").inner_text()
                
                # Extract potential resume/CV PDF links on this profile page
                cv_links = []
                anchors = page.locator("a[href]")
                for a_idx in range(anchors.count()):
                    a_elem = anchors.nth(a_idx)
                    a_href = a_elem.get_attribute("href")
                    a_text = a_elem.inner_text().lower()
                    if a_href and ('pdf' in a_href.lower() or 'cv' in a_text or 'resume' in a_text):
                        full_cv_url = a_href if a_href.startswith("http") else BASE_DOMAIN + a_href
                        cv_links.append(full_cv_url)

                # Parse lines for structured attributes
                lines = [line.strip() for line in body_text.split('\n') if line.strip()]
                
                name = lines[0] if len(lines) > 0 else "Unknown"
                
                detailed_faculty_list.append({
                    "profile_url": profile_url,
                    "raw_text_corpus": body_text, # This full text will be embedded for deep LLM retrieval!
                    "cv_resume_links": cv_links
                })
                
            except Exception as e:
                print(f"Failed to crawl {profile_url}: {e}")
                
        browser.close()

    # Save the deep dataset
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "faculty_deep_profiles.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(detailed_faculty_list, f, indent=4, ensure_ascii=False)
        
    print(f"SUCCESS: Deep-scraped {len(detailed_faculty_list)} professor profiles with full text & CV links.")
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    deep_scrape_faculty()