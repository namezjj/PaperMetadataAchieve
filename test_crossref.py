import os
import requests
from datetime import datetime
from pprint import pprint
from typing import Dict, List, Any, Optional

def _format_date(date_data: Dict[str, Any]) -> str:
    """Format publication date from CrossRef data"""
    if not date_data or 'date-parts' not in date_data:
        return ''
        
    try:
        date_parts = date_data['date-parts'][0]
        if len(date_parts) >= 3:
            return datetime(*date_parts[:3]).strftime('%Y-%m-%d')
        elif len(date_parts) == 2:
            return datetime(*date_parts, 1).strftime('%Y-%m')
        elif len(date_parts) == 1:
            return str(date_parts[0])
        return ''
    except Exception:
        return ''

def get_paper_info(doi: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive paper metadata from CrossRef API using a DOI.
    
    Args:
        doi (str): The DOI of the paper to look up
        
    Returns:
        dict: Comprehensive metadata including:
            - DOI
            - Title
            - Abstract
            - Authors (names, affiliations, ORCID, sequence)
            - Subject/Field
            - Journal info
            - Publication date
            - Citation metrics
            - Article type
            - Funding information
            - References
    """
    email = os.getenv("CROSSREF_EMAIL", "your-email@example.com")
        
    headers = {
        "User-Agent": f"PaperExtractor/1.0 (mailto:{email})",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(
            f"https://api.crossref.org/works/{doi}",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()['message']
        
        # Extract author information
        authors_data = {
            'names': [],
            'sequences': [],
            'orcids': [],
            'affiliations': []
        }
        
        for author in data.get('author', []):
            authors_data['names'].append(
                f"{author.get('given', '')} {author.get('family', '')}".strip()
            )
            authors_data['sequences'].append(author.get('sequence', ''))
            authors_data['orcids'].append(author.get('ORCID', ''))
            
            author_affiliations = []
            if 'affiliation' in author:
                for affiliation in author['affiliation']:
                    if isinstance(affiliation, dict):
                        author_affiliations.append(affiliation.get('name', ''))
            authors_data['affiliations'].append(author_affiliations)

        # Build comprehensive metadata
        metadata = {
            'identifier': {
                'doi': data.get('DOI', ''),
                'url': f"https://doi.org/{data.get('DOI', '')}"
            },
            'title': data.get('title', [''])[0] if data.get('title') else '',
            'abstract': data.get('abstract', ''),
            'authors': {
                'names': authors_data['names'],
                'sequences': authors_data['sequences'],
                'orcids': authors_data['orcids'],
                'affiliations': authors_data['affiliations']
            },
            'subject_areas': data.get('subject', []),
            'journal': {
                'name': data.get('container-title', [''])[0] if data.get('container-title') else '',
                'issn': data.get('ISSN', []),
                'type': data.get('type', ''),
                'impact_factor': 'Not available via CrossRef',
                'quartile': 'Not available via CrossRef'
            },
            'publication': {
                'type': data.get('type', ''),
                'date': _format_date(data.get('published-print', data.get('published-online', {}))),
                'citations': data.get('is-referenced-by-count', 0)
            },
            'references': [
                ref.get('DOI', '') for ref in data.get('reference', []) if ref.get('DOI')
            ],
            'funding': [
                {
                    'funder': funder.get('name', ''),
                    'award': funder.get('award', [])
                }
                for funder in data.get('funder', [])
            ]
        }
            
        return metadata
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            "message": str(e)
        }

def format_output(metadata: Dict[str, Any]) -> None:
    """Format and print metadata in a structured way"""
    print("\nPaper Information")
    print("=" * 50)
    
    # Basic Information
    print("\nBasic Information:")
    print(f"DOI: {metadata['identifier']['doi']}")
    print(f"URL: {metadata['identifier']['url']}")
    print(f"Title: {metadata['title']}")
    
    # Authors
    print("\nAuthors:")
    if metadata['authors']['names']:
        for i, (name, orcid, sequence, affiliations) in enumerate(zip(
            metadata['authors']['names'],
            metadata['authors']['orcids'],
            metadata['authors']['sequences'],
            metadata['authors']['affiliations']
        ), 1):
            # Add corresponding author indicator
            is_corresponding = sequence == 'additional' or sequence == 'last'  # Usually the last or additional author is corresponding
            author_type = " [Corresponding Author]" if is_corresponding else ""
            
            print(f"\n{i}. {name}{author_type}")
            print(f"   ORCID: {orcid if orcid else 'Not available'}")
            print(f"   Sequence: {sequence if sequence else 'Not available'}")
            print("   Affiliations:")
            if affiliations:
                for aff in affiliations:
                    print(f"   - {aff}")
            else:
                print("   - None listed")
    else:
        print("No authors listed")
    
    # Journal Information
    print("\nJournal Information:")
    print(f"Name: {metadata['journal']['name'] or 'Not available'}")
    print(f"Type: {metadata['journal']['type'] or 'Not available'}")
    print(f"ISSN: {', '.join(metadata['journal']['issn']) if metadata['journal']['issn'] else 'Not available'}")
    print(f"Impact Factor: {metadata['journal']['impact_factor']}")
    print(f"Quartile: {metadata['journal']['quartile']}")
    
    # Publication Details
    print("\nPublication Details:")
    print(f"Type: {metadata['publication']['type'] or 'Not available'}")
    print(f"Date: {metadata['publication']['date'] or 'Not available'}")
    print(f"Citation Count: {metadata['publication']['citations']}")
    
    # Subject Areas
    print("\nSubject Areas:")
    if metadata['subject_areas']:
        for subject in metadata['subject_areas']:
            print(f"- {subject}")
    else:
        print("No subject areas listed")
    
    # Abstract
    print("\nAbstract:")
    if metadata['abstract']:
        print(metadata['abstract'])
    else:
        print("No abstract available")
    
    # Funding Information
    print("\nFunding Information:")
    if metadata['funding']:
        for fund in metadata['funding']:
            print(f"Funder: {fund['funder']}")
            if fund['award']:
                print(f"Awards: {', '.join(fund['award'])}")
            else:
                print("Awards: None listed")
    else:
        print("No funding information available")
    
    # References
    print("\nReferences:")
    if metadata['references']:
        print(f"Total number of references with DOIs: {len(metadata['references'])}")
        print("\nFirst 5 reference DOIs:")
        for ref in metadata['references'][:5]:
            print(f"- {ref}")
        if len(metadata['references']) > 5:
            print(f"... and {len(metadata['references']) - 5} more")
    else:
        print("No references with DOIs available")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    # Test a single DOI
    test_doi = "10.1016/j.commatsci.2009.03.015"
    
    print(f"Retrieving metadata for DOI: {test_doi}")
    print("-" * 50)
    
    result = get_paper_info(test_doi)
    
    if "status" in result and result["status"] == "error":
        print(f"Error: {result['message']}")
    else:
        format_output(result) 