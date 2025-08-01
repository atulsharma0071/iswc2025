# Indus Script Knowledge Graph Generator

![GUI Screenshot](screenshot.png) <!-- Add a screenshot later -->

A semantic tool for analyzing and comparing ancient scripts with a focus on the Indus Valley script. This application generates a knowledge graph from script symbols, enables SPARQL querying, and provides visualization capabilities.

## Version Comparison

### Version 2 Features
- **Enhanced Metrics Dashboard**: Track KG generation time, query performance, and error counts
- **Progress Tracking**: Visual progress bar for KG generation
- **Improved Performance Monitoring**: Detailed timing metrics for all operations
- **Advanced Error Handling**: Better error tracking and user notifications
- **Optimized KG Generation**: More efficient processing of script data

### Version 1 Features
- **Core Knowledge Graph Generation**: Creates RDF-based knowledge graph from script symbol images
- **Basic SPARQL Interface**: Execute and visualize SPARQL queries
- **Multiple Export Formats**: Turtle, RDF/XML, JSON-LD
- **Linked Data Publishing**: Generate HTML portal for published datasets
- **VoID Description**: Create dataset metadata descriptions
- **Cross-Script Analysis**: Compare Indus script with other ancient scripts

## Supported Scripts
- Indus Valley
- Ba-Shu
- Naxi Dongba
- Old Naxi
- Proto-Cuneiform  
- Proto-Elamite
- Standard Yi
- Yi

## Installation

### Prerequisites
- Python 3.7+
- Required packages:
  ```bash
  pip install rdflib tkinter matplotlib numpy opencv-python-headless
Getting Started
Clone the repository:

bash
git clone https://github.com/yourusername/indus-script-kg.git
cd indus-script-kg
Install dependencies:

bash
pip install -r requirements.txt
Download the dataset:

Place script symbol images in folders under an ind directory

Structure:

text
ind/
├── indus/
│   ├── symbol1.png
│   ├── symbol2.jpg
│   └── ...
├── ba-shu/
├── naxi_dongba/
└── ...
Run the application:

bash
# For Version 1
python semantic_script_analyzer_v1.py

# For Version 2 
python semantic_script_analyzer_v2.py
Usage Guide
Knowledge Graph Generation
Select dataset folder containing script images

Choose primary script (default: Indus)

Select one or more comparison scripts

Click "Generate Knowledge Graph"

View statistics in the "KG Statistics" tab

SPARQL Querying
Use the SPARQL tab to run queries

Try built-in example queries for common analyses

Export results as CSV or RDF

Export Options
Knowledge Graph: Export full KG in Turtle, RDF/XML, or JSON-LD

Linked Data: Publish as FAIR data with HTML portal

VoID: Generate dataset metadata description

Example SPARQL Queries
sparql
# Get most frequent Indus symbols
PREFIX script: <http://example.org/scripts#>
SELECT ?symbol ?freq WHERE {
  ?symbol a script:Symbol ;
          script:fromScript "indus" ;
          script:symbolFrequency ?freq .
}
ORDER BY DESC(?freq)
LIMIT 10

# Find similar symbols across scripts  
PREFIX script: <http://example.org/scripts#>
SELECT ?indusSymbol ?otherSymbol ?script ?score WHERE {
  ?indusSymbol script:fromScript "indus" ;
               script:similarTo ?otherSymbol ;
               script:similarityScore ?score .
  ?otherSymbol script:fromScript ?script .
  FILTER (?script != "indus")
}
ORDER BY DESC(?score)
Version History
v2.0 (Current)
Added comprehensive metrics dashboard

Implemented progress tracking

Enhanced error handling

Improved performance monitoring

Optimized KG generation

v1.0
Initial release with core functionality

Basic KG generation from script images

SPARQL query interface

Multiple export formats

Linked Data publishing

Contributing
Contributions welcome! Please:

Fork the repository

Create a feature branch

Submit a pull request
