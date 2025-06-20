import os
import csv
import json
from tqdm import tqdm
from typing import Dict, Any, List
import time
from pathlib import Path
from datetime import datetime

# Import functions from test_crossref
from test_crossref import get_paper_info, format_output
from io import StringIO
import sys

def process_dois_to_json(csv_path: str, output_path: str) -> None:
    """
    Process DOIs and save comprehensive results in JSON format
    
    Args:
        csv_path (str): Path to CSV file containing DOIs
        output_path (str): Path to save JSON output
    """
    # Read DOIs from CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        dois = [row[0] for row in reader]

    # Initialize results structure
    results = {
        'metadata': {
            'extraction_date': datetime.now().isoformat(),
            'total_dois': len(dois),
            'source_file': csv_path
        },
        'papers': []
    }
    
    for doi in tqdm(dois, desc="Retrieving metadata"):
        doi = doi.strip()
        if not doi:
            continue
            
        try:
            result = get_paper_info(doi)
            
            if "status" in result and result["status"] == "error":
                paper_data = {
                    'doi': doi,
                    'status': 'error',
                    'error_message': result['message'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Restructure author information for better clarity
                authors_info = []
                for i, (name, orcid, sequence, affiliations) in enumerate(zip(
                    result['authors']['names'],
                    result['authors']['orcids'],
                    result['authors']['sequences'],
                    result['authors']['affiliations']
                ), 1):
                    author_data = {
                        'index': i,
                        'name': name,
                        'orcid': orcid if orcid else None,
                        'sequence': sequence,
                        'is_corresponding': sequence == 'additional' or sequence == 'last',
                        'affiliations': affiliations if affiliations else []
                    }
                    authors_info.append(author_data)

                paper_data = {
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'paper': {
                        'identifier': {
                            'doi': result['identifier']['doi'],
                            'url': result['identifier']['url']
                        },
                        'title': result['title'],
                        'abstract': result['abstract'],
                        'authors': authors_info,
                        'publication': {
                            'journal': {
                                'name': result['journal']['name'],
                                'issn': result['journal']['issn'],
                                'type': result['journal']['type'],
                                'impact_factor': result['journal']['impact_factor'],
                                'quartile': result['journal']['quartile']
                            },
                            'type': result['publication']['type'],
                            'date': result['publication']['date'],
                            'citations': result['publication']['citations']
                        },
                        'subject_areas': result['subject_areas'],
                        'references': {
                            'count': len(result['references']),
                            'dois': result['references']
                        },
                        'funding': [
                            {
                                'funder': fund['funder'],
                                'awards': fund['award']
                            }
                            for fund in result['funding']
                        ]
                    }
                }
            
            results['papers'].append(paper_data)
            time.sleep(1)
            
        except Exception as e:
            paper_data = {
                'doi': doi,
                'status': 'error',
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            results['papers'].append(paper_data)

    # Add summary information
    results['summary'] = {
        'successful_extractions': sum(1 for p in results['papers'] if p.get('status') == 'success'),
        'failed_extractions': sum(1 for p in results['papers'] if p.get('status') == 'error'),
        'completion_time': datetime.now().isoformat()
    }

    # Save as JSON with proper formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    csv_path = r'/Users/zjj_macbook/Desktop/Work/DPT/paperextractor-master/transinfo/transinfo/utils/ele_dois.csv'
    output_json = r'/Users/zjj_macbook/Desktop/Work/DPT/paperextractor-master/transinfo/transinfo/utils/metadate.json'
    process_dois_to_json(csv_path, output_json)
    print(f"Extraction complete! Results saved in: {output_json}")
