import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

def process_json_to_excel(json_path: str, output_excel: str) -> None:
    """
    Convert JSON metadata to Excel format with simplified reference information
    
    Args:
        json_path (str): Path to the JSON metadata file
        output_excel (str): Path to save the Excel file
    """
    # Read JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract paper information
    papers_data = []
    
    for paper in data['papers']:
        if paper['status'] != 'success':
            continue
            
        paper_info = paper['paper']
        
        # Process authors information
        authors = paper_info['authors']
        
        # Get corresponding authors
        corresponding_authors = [
            author['name'] for author in authors 
            if author['is_corresponding']
        ]
        
        # Create entry for each paper
        entry = {
            'DOI': paper_info['identifier']['doi'],
            'Title': paper_info['title'],
            'Abstract': paper_info['abstract'],
            
            # Authors information
            'Author Count': len(authors),
            'Authors': f"[{', '.join(author['name'] for author in authors)}]",
            'Author Sequences': f"[{', '.join(author['sequence'] for author in authors)}]",
            'Corresponding Authors': f"[{', '.join(corresponding_authors)}]" if corresponding_authors else '[]',
            'Author ORCIDs': f"[{', '.join(author['orcid'] if author['orcid'] else '' for author in authors)}]",
            'Author Affiliations': f"[{', '.join(f'{author['name']}: {', '.join(author['affiliations'])}' for author in authors if author['affiliations'])}]" if any(author['affiliations'] for author in authors) else '[]',
            
            # Journal information
            'Journal': paper_info['publication']['journal']['name'],
            'Journal Type': paper_info['publication']['journal']['type'],
            'ISSN': f"[{', '.join(paper_info['publication']['journal']['issn'])}]" if paper_info['publication']['journal']['issn'] else '[]',
            
            # Publication details
            'Publication Date': paper_info['publication']['date'],
            'Article Type': paper_info['publication']['type'],
            'Citation Count': paper_info['publication']['citations'],
            
            # Subject areas
            'Subject Areas': f"[{', '.join(paper_info['subject_areas'])}]" if paper_info['subject_areas'] else '[]',
            
            # Reference counts
            'Reference Count': paper_info['references']['count'],
            
            # Funding information
            'Funders': f"[{', '.join(f'{fund['funder']} ({', '.join(fund['awards']) if fund['awards'] else 'no award info'}' for fund in paper_info['funding'])}]" if paper_info['funding'] else '[]'
        }
        
        papers_data.append(entry)

    # Convert to DataFrame
    df = pd.DataFrame(papers_data)
    
    # Reorder columns for better readability
    column_order = [
        'DOI',
        'Title',
        'Abstract',
        'Author Count',
        'Authors',
        'Author Sequences',
        'Corresponding Authors',
        'Author ORCIDs',
        'Author Affiliations',
        'Journal',
        'Journal Type',
        'ISSN',
        'Publication Date',
        'Article Type',
        'Citation Count',
        'Subject Areas',
        'Reference Count',
        'Funders'
    ]
    
    df = df[column_order]
    
    # Save to Excel with formatting
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Paper Metadata')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Paper Metadata']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

    print(f"Excel file created successfully: {Path(output_excel).resolve()}")
    print(f"Total papers processed: {len(papers_data)}")

if __name__ == "__main__":
    json_path = r"/Users/zjj_macbook/Desktop/Work/DPT/paperextractor-master/transinfo/transinfo/utils/metadate.json"  # Input JSON file
    output_excel = "paper_metadata.xlsx"  # Output Excel file in current directory
    process_json_to_excel(json_path, output_excel)