# Indus Script Knowledge Graph Generator

![GUI Screenshot]
<img width="1190" height="768" alt="v21" src="https://github.com/user-attachments/assets/5947fd4d-6dc9-434d-8a76-2f7cfefa9040" />
<!-- Add a screenshot later -->

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
1. Added comprehensive metrics dashboard

2. Implemented progress tracking

3. Enhanced error handling

4. Improved performance monitoring

5. Optimized KG generation

v1.0
1. Initial release with core functionality

2. Basic KG generation from script images

3. SPARQL query interface

4. Multiple export formats

5. Linked Data publishing

Contributing
Contributions welcome! Please:

Fork the repository



## Dataset Information

The script symbol images are sourced from the [IVC2TYC repository](https://github.com/oohalakkadi/ivc2tyc/tree/main/datasets) by [oohalakkadi](https://github.com/oohalakkadi). 

### Getting the Dataset

1. **Option 1**: Clone the entire repository
   ```bash
   git clone https://github.com/oohalakkadi/ivc2tyc.git
   cp -r ivc2tyc/datasets/ind ./ind




   
