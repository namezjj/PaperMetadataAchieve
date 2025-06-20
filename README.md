Project Introduction
PaperMetadataAchieve is a simple toolset for batch retrieval of academic paper metadata, saving the raw JSON, and generating structured tables. Users only need to prepare a CSV file containing DOIs; the program automatically pulls complete metadata from the CrossRef API and generates tables ready for further analysis.

Function Overview
Batch DOI Processing
Read the DOI list from a CSV file and automatically retrieve metadata for each paper.

Metadata JSON Saving
Use the metadata_get script to batch download CrossRef metadata for each DOI and save it as .json files for easy tracking and reuse.

Structured Table Generation
Run the metadata_excel script to extract key information (such as title, authors, journal, publication date, citation count, etc.) from the raw JSON and organize it into a structured Excel or CSV table for data analysis and visualization.

View Raw Metadata
The raw_crossref script is used to quickly inspect all fields returned by the CrossRef API, helping you understand the available metadata content and structure.
