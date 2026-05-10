import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

# Define the target directory (relative to this script's location)
RAW_PAPERS_DIR = Path(__file__).resolve().parent.parent / "01_raw_papers"

def fetch_arxiv_title(arxiv_id: str) -> str:
    """Queries the ArXiv API to fetch the official title of a paper."""
    try:
        # The ArXiv API is free and doesn't require a key
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        response = urllib.request.urlopen(url, timeout=10)
        xml_data = response.read()
        
        # Parse the XML response
        root = ET.fromstring(xml_data)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Find the first entry and its title
        entry = root.find('atom:entry', namespace)
        if entry is not None:
            title = entry.find('atom:title', namespace).text
            # Clean up the title (ArXiv sometimes includes line breaks)
            clean_title = re.sub(r'\s+', ' ', title).strip()
            # Remove characters that are illegal in file names
            clean_title = re.sub(r'[\\/*?:"<>|]', "", clean_title)
            return clean_title
    except Exception as e:
        print(f"  [!] Failed to fetch ArXiv metadata for {arxiv_id}: {e}")
    
    return ""

def clean_filename(filename: str) -> str:
    """Cleans a messy filename into a readable Title Case format."""
    # 1. URL Decode (fixes %20 -> space)
    name = urllib.parse.unquote(filename)
    
    # 2. Strip out "v1", "v2" versioning artifacts often found at the end of names
    name = re.sub(r'v\d+$', '', name, flags=re.IGNORECASE)
    
    # 3. Strip out common junk like "FINAL", "draft"
    name = re.sub(r'(_|-)?(final|draft|\(\d+\))', '', name, flags=re.IGNORECASE)
    
    # 4. Replace underscores and hyphens with spaces
    name = name.replace("_", " ").replace("-", " ")
    
    # 5. Remove multiple spaces and apply Title Case
    name = " ".join(name.split()).title()
    
    return name

def run_standardization():
    print("========================================")
    print(" Axiom Alpha: PDF Standardization Engine")
    print("========================================\n")
    
    if not RAW_PAPERS_DIR.exists():
        print(f"Directory not found: {RAW_PAPERS_DIR}")
        return

    processed = 0
    
    # Regex to detect standard ArXiv IDs (e.g., 2103.14322 or 2103.14322v2)
    arxiv_pattern = re.compile(r'^(\d{4}\.\d{4,5})(v\d+)?$')

    for file in os.listdir(RAW_PAPERS_DIR):
        if not file.lower().endswith(".pdf"):
            continue

        original_path = RAW_PAPERS_DIR / file
        stem = original_path.stem  # Filename without the .pdf extension
        new_name = ""

        # Check if the filename is an ArXiv ID
        arxiv_match = arxiv_pattern.match(stem)
        
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
            print(f"[*] Detected ArXiv ID: {arxiv_id}. Fetching metadata...")
            new_name = fetch_arxiv_title(arxiv_id)

        # If it wasn't an ArXiv ID, or the API call failed, fall back to regex cleaning
        if not new_name:
            new_name = clean_filename(stem)

        # Skip if the name hasn't meaningfully changed
        if new_name.lower() == stem.lower():
            continue

        # Construct new path
        new_filename = f"{new_name}.pdf"
        new_path = RAW_PAPERS_DIR / new_filename

        # Handle edge case where the renamed file already exists
        counter = 1
        while new_path.exists():
            new_path = RAW_PAPERS_DIR / f"{new_name} ({counter}).pdf"
            counter += 1

        # Execute the rename
        original_path.rename(new_path)
        print(f"  [+] Renamed: '{file}' -> '{new_path.name}'")
        processed += 1

    if processed == 0:
        print("All PDFs are already standardized.")
    else:
        print(f"\n✅ Standardized {processed} PDF(s). Ready for NotebookLM upload.")

if __name__ == "__main__":
    run_standardization()