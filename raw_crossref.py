import requests
import json
from pprint import pprint

def get_raw_crossref_data(doi: str) -> None:
    """Get and display raw metadata from Crossref API"""
    headers = {
        "User-Agent": "PaperExtractor/1.0 (mailto:your-email@example.com)",
        "Accept": "application/json"
    }
    
    response = requests.get(
        f"https://api.crossref.org/works/{doi}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        # Pretty print the raw data with proper indentation
        print("\nRaw Crossref Metadata:")
        print("=" * 80)
        pprint(data['message'], indent=2, width=120, sort_dicts=False)
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Example DOI
    test_doi = "10.1021/jp206881t"
    
    print(f"Fetching raw metadata for DOI: {test_doi}")
    get_raw_crossref_data(test_doi) 