import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, PROV, DCTERMS
from rdflib.plugins.sparql import prepareQuery
import os
import numpy as np
import cv2
from datetime import datetime
import webbrowser
import csv

class SemanticScriptAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Indus Script Knowledge Graph Generator")
        self.root.geometry("1200x800")
        
        # Script folders
        self.script_folders = ['indus', 'ba-shu', 'naxi_dongba', 'old_naxi',
                             'proto_cuneiform', 'proto_elamite', 'standard_yi', 'yi']
        
        # Initialize KG and ontology
        self.kg = Graph()
        self.ns = Namespace("http://example.org/scripts#")
        self.define_ontology()
        
        # Create UI
        self.create_widgets()
        
        # Set default dataset path
        self.dataset_path = os.path.join(os.getcwd(), 'ind')
        if not os.path.exists(self.dataset_path):
            messagebox.showwarning("Warning", "'ind' dataset folder not found")

    def define_ontology(self):
        """Enhanced ontology with PROV-O support"""
        self.kg.bind("script", self.ns)
        self.kg.bind("prov", PROV)
        self.kg.bind("dcterms", DCTERMS)
        
        # Core classes
        classes = [
            (self.ns.Script, "Ancient writing system"),
            (self.ns.Symbol, "Individual character/glyph"),
            (self.ns.ScriptFamily, "Group of related scripts")
        ]
        
        for cls, comment in classes:
            self.kg.add((cls, RDF.type, OWL.Class))
            self.kg.add((cls, RDFS.comment, Literal(comment)))
        
        # Properties
        properties = [
            (self.ns.hasSymbol, "Script contains symbol", OWL.ObjectProperty),
            (self.ns.similarTo, "Similarity relationship", OWL.ObjectProperty),
            (self.ns.similarityScore, "Numerical similarity", OWL.DatatypeProperty),
            (self.ns.scriptFamily, "Family classification", OWL.ObjectProperty),
            (self.ns.symbolFrequency, "Usage frequency", OWL.DatatypeProperty),
            (self.ns.contourCount, "Number of contours in glyph", OWL.DatatypeProperty),
            (self.ns.fromScript, "Indicates source script", OWL.DatatypeProperty)
        ]
        
        for prop, comment, prop_type in properties:
            self.kg.add((prop, RDF.type, prop_type))
            self.kg.add((prop, RDFS.comment, Literal(comment)))
        
        # Define script families
        self.kg.add((self.ns.IndusValleyFamily, RDF.type, self.ns.ScriptFamily))
        self.kg.add((self.ns.ProtoElamiteFamily, RDF.type, self.ns.ScriptFamily))

    def create_widgets(self):
        """Build the UI interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Dataset selection
        ttk.Label(control_frame, text="Dataset Path:").pack(pady=5)
        self.dataset_entry = ttk.Entry(control_frame)
        self.dataset_entry.pack(fill=tk.X, pady=5)
        self.dataset_entry.insert(0, os.path.join(os.getcwd(), 'ind'))
        
        ttk.Button(control_frame, text="Browse...", 
                  command=self.browse_dataset).pack(pady=5)
        
        # Script selection
        ttk.Label(control_frame, text="Primary Script:").pack(pady=5)
        self.primary_script = ttk.Combobox(control_frame, values=self.script_folders)
        self.primary_script.set("indus")
        self.primary_script.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Comparison Script(s):").pack(pady=5)
        self.comparison_scripts = tk.Listbox(control_frame, selectmode=tk.MULTIPLE, height=6)
        for script in [s for s in self.script_folders if s != "indus"]:
            self.comparison_scripts.insert(tk.END, script)
        self.comparison_scripts.pack(fill=tk.X, pady=5)
        
        # KG Generation button
        ttk.Button(control_frame, text="Generate Knowledge Graph", 
                  command=self.generate_kg).pack(pady=15, fill=tk.X)
        
        # Export buttons
        ttk.Label(control_frame, text="Export:").pack(pady=5)
        ttk.Button(control_frame, text="Export KG (Turtle)", 
                  command=self.export_kg).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Publish as Linked Data", 
                  command=self.publish_as_linked_data).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Generate VoID Description", 
                  command=self.generate_void_description).pack(fill=tk.X, pady=5)
        
        # Right panel - Results display
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook for multiple views
        self.results_notebook = ttk.Notebook(result_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # KG Statistics tab
        self.stats_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.stats_tab, text="KG Statistics")
        self.stats_output = tk.Text(self.stats_tab, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.stats_tab, command=self.stats_output.yview)
        self.stats_output.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_output.pack(fill=tk.BOTH, expand=True)
        
        # SPARQL Query tab
        self.create_sparql_tab()
        
        # Status bar
        self.status = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def create_sparql_tab(self):
        """Create SPARQL query interface with enhanced output"""
        self.sparql_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.sparql_tab, text="SPARQL Query")
        
        # Query input
        ttk.Label(self.sparql_tab, text="SPARQL Query:").pack(pady=5)
        self.query_text = tk.Text(self.sparql_tab, height=10, wrap=tk.WORD)
        self.query_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Query buttons
        button_frame = ttk.Frame(self.sparql_tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="Execute", command=self.execute_sparql).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Clear", command=self.clear_sparql).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Example Queries", command=self.show_sparql_examples).pack(side=tk.RIGHT)
        
        # Results display
        ttk.Label(self.sparql_tab, text="Results:").pack(pady=5)
        self.query_results = tk.Text(self.sparql_tab, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.sparql_tab, command=self.query_results.yview)
        self.query_results.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.query_results.pack(fill=tk.BOTH, expand=True)
        
        # Export buttons
        export_frame = ttk.Frame(self.sparql_tab)
        export_frame.pack(fill=tk.X)
        ttk.Button(export_frame, text="Export as CSV", 
                  command=self.export_sparql_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export as RDF", 
                  command=self.export_sparql_rdf).pack(side=tk.LEFT)

    def browse_dataset(self):
        """Let user select dataset directory"""
        path = filedialog.askdirectory()
        if path:
            self.dataset_entry.delete(0, tk.END)
            self.dataset_entry.insert(0, path)

    def generate_kg(self):
        """Generate knowledge graph from selected scripts"""
        self.dataset_path = self.dataset_entry.get()
        primary = self.primary_script.get()
        comparisons = [self.comparison_scripts.get(i) for i in self.comparison_scripts.curselection()]
        
        if not comparisons:
            messagebox.showwarning("Warning", "Please select at least one comparison script")
            return
        
        self.status.config(text="Generating Knowledge Graph...")
        self.root.update()
        
        try:
            # Reinitialize KG
            self.kg = Graph()
            self.define_ontology()
            
            # Load script data
            self.load_script_data(primary, comparisons)
            
            # Display statistics
            self.display_kg_statistics()
            self.status.config(text="KG generation complete")
        except Exception as e:
            messagebox.showerror("Error", f"KG generation failed: {str(e)}")
            self.status.config(text="KG generation failed")

    def load_script_data(self, primary, comparisons):
        """Load script data and build KG"""
        for script in [primary] + comparisons:
            script_path = os.path.join(self.dataset_path, script)
            if not os.path.exists(script_path):
                continue
                
            script_uri = self.ns[script]
            self.kg.add((script_uri, RDF.type, self.ns.Script))
            self.kg.add((script_uri, RDFS.label, Literal(script)))
            self.kg.add((script_uri, self.ns.fromScript, Literal(script)))
            
            # Add to script family
            if script == "indus":
                self.kg.add((script_uri, self.ns.scriptFamily, self.ns.IndusValleyFamily))
            elif script == "proto_elamite":
                self.kg.add((script_uri, self.ns.scriptFamily, self.ns.ProtoElamiteFamily))
            
            # Process each symbol image
            for img_file in os.listdir(script_path):
                if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    symbol_id = os.path.splitext(img_file)[0]
                    symbol_uri = self.ns[f"{script}_{symbol_id}"]
                    
                    # Add to KG
                    self.kg.add((symbol_uri, RDF.type, self.ns.Symbol))
                    self.kg.add((symbol_uri, RDFS.label, Literal(symbol_id)))
                    self.kg.add((symbol_uri, self.ns.fromScript, Literal(script)))
                    self.kg.add((script_uri, self.ns.hasSymbol, symbol_uri))
                    
                    # Add simulated data
                    freq = np.random.randint(1, 100)
                    self.kg.add((symbol_uri, self.ns.symbolFrequency, Literal(freq, datatype=XSD.integer)))
                    
                    # Add simulated visual features
                    img = cv2.imread(os.path.join(script_path, img_file), cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        contours = np.random.randint(1, 10)
                        self.kg.add((symbol_uri, self.ns.contourCount, Literal(contours, datatype=XSD.integer)))
                        
                        # Add some similarity relationships
                        if script == primary and np.random.random() > 0.7:
                            for comp_script in comparisons:
                                comp_symbol = f"{comp_script}_symbol_{np.random.randint(1,50)}"
                                score = round(np.random.uniform(0.5, 0.95), 2)
                                self.kg.add((
                                    symbol_uri,
                                    self.ns.similarTo,
                                    self.ns[comp_symbol]
                                ))
                                self.kg.add((
                                    symbol_uri,
                                    self.ns.similarityScore,
                                    Literal(score, datatype=XSD.float)
                                ))

    def display_kg_statistics(self):
        """Display KG statistics in the stats tab"""
        self.stats_output.delete(1.0, tk.END)
        
        # Basic stats
        self.stats_output.insert(tk.END, "=== Knowledge Graph Statistics ===\n\n")
        self.stats_output.insert(tk.END, f"Total Triples: {len(self.kg)}\n")
        self.stats_output.insert(tk.END, f"Scripts: {len(list(self.kg.subjects(RDF.type, self.ns.Script)))}\n")
        self.stats_output.insert(tk.END, f"Symbols: {len(list(self.kg.subjects(RDF.type, self.ns.Symbol)))}\n")
        
        # Sample data
        self.stats_output.insert(tk.END, "\n=== Sample Triples ===\n\n")
        for s, p, o in list(self.kg)[:5]:  # Show first 5 triples
            self.stats_output.insert(tk.END, f"{s.n3()} {p.n3()} {o.n3()}\n")

    def execute_sparql(self):
        """Execute SPARQL query with comprehensive output handling"""
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a SPARQL query")
            return
        
        try:
            # Clear previous results
            self.query_results.delete(1.0, tk.END)
            
            # Execute query
            results = self.kg.query(query)
            
            # Display based on query type
            if results.type == "SELECT":
                self.display_select_results(results)
            elif results.type == "CONSTRUCT":
                self.display_construct_results(results)
            elif results.type == "ASK":
                self.display_ask_result(results)
            elif results.type == "DESCRIBE":
                self.display_describe_results(results)
            else:
                self.query_results.insert(tk.END, f"Unsupported query type: {results.type}\n")
                
        except Exception as e:
            messagebox.showerror("SPARQL Error", f"Query execution failed: {str(e)}")
            self.query_results.insert(tk.END, f"Error: {str(e)}\n")

    def display_select_results(self, results):
        """Format SELECT query results as a table"""
        # Get headers
        headers = results.vars
        header_row = "\t".join(str(h) for h in headers) + "\n"
        separator = "-" * (len(header_row)*2) + "\n"
        
        # Add to output
        self.query_results.insert(tk.END, header_row)
        self.query_results.insert(tk.END, separator)
        
        # Add rows
        for row in results:
            row_str = "\t".join(str(val) if val else "NULL" for val in row) + "\n"
            self.query_results.insert(tk.END, row_str)
        
        # Add summary
        self.query_results.insert(tk.END, f"\n{len(results)} results\n")

    def display_construct_results(self, results):
        """Format CONSTRUCT query results"""
        self.query_results.insert(tk.END, "Constructed Triples:\n\n")
        for triple in results:
            self.query_results.insert(tk.END, f"{triple}\n")
        self.query_results.insert(tk.END, f"\n{len(results)} triples constructed\n")

    def display_ask_result(self, results):
        """Format ASK query result"""
        self.query_results.insert(tk.END, f"ASK Query Result: {results.askAnswer}\n")

    def display_describe_results(self, results):
        """Format DESCRIBE query results"""
        self.query_results.insert(tk.END, "Description Results:\n\n")
        for triple in results:
            self.query_results.insert(tk.END, f"{triple}\n")
        self.query_results.insert(tk.END, f"\n{len(results)} triples in description\n")

    def export_sparql_csv(self):
        """Export SPARQL SELECT results as CSV"""
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "No query to execute")
            return
            
        try:
            results = self.kg.query(query)
            if results.type != "SELECT":
                messagebox.showwarning("Warning", "Only SELECT queries can be exported to CSV")
                return
                
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save SPARQL results as CSV"
            )
            
            if file_path:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([str(var) for var in results.vars])
                    for row in results:
                        writer.writerow([str(val) for val in row])
                messagebox.showinfo("Success", f"Results saved to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def export_sparql_rdf(self):
        """Export SPARQL CONSTRUCT/DESCRIBE results as RDF"""
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "No query to execute")
            return
            
        try:
            results = self.kg.query(query)
            if results.type not in ["CONSTRUCT", "DESCRIBE"]:
                messagebox.showwarning("Warning", "Only CONSTRUCT/DESCRIBE queries can be exported as RDF")
                return
                
            file_path = filedialog.asksaveasfilename(
                defaultextension=".ttl",
                filetypes=[("Turtle files", "*.ttl"), ("RDF/XML", "*.rdf")],
                title="Save SPARQL results as RDF"
            )
            
            if file_path:
                result_graph = Graph()
                for triple in results:
                    result_graph.add(triple)
                
                format = "turtle" if file_path.endswith(".ttl") else "xml"
                result_graph.serialize(destination=file_path, format=format)
                messagebox.showinfo("Success", f"Results saved to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def clear_sparql(self):
        """Clear the SPARQL query and results"""
        self.query_text.delete(1.0, tk.END)
        self.query_results.delete(1.0, tk.END)

    def show_sparql_examples(self):
        """Show Indus-focused SPARQL query examples"""
        examples = """# 1. Basic Symbol Inventory
PREFIX script: <http://example.org/scripts#>
SELECT ?symbol ?freq WHERE {
  ?symbol a script:Symbol ;
          script:fromScript "indus" ;
          script:symbolFrequency ?freq .
}
ORDER BY DESC(?freq)
LIMIT 10

# 2. Cross-Script Similarity
PREFIX script: <http://example.org/scripts#>
SELECT ?indusSymbol ?otherSymbol ?script ?score WHERE {
  ?indusSymbol script:fromScript "indus" ;
               script:similarTo ?otherSymbol ;
               script:similarityScore ?score .
  ?otherSymbol script:fromScript ?script .
  FILTER (?script != "indus")
}
ORDER BY DESC(?score)
LIMIT 5

# 3. Complex Glyph Identification
PREFIX script: <http://example.org/scripts#>
SELECT ?symbol ?contours WHERE {
  ?symbol script:fromScript "indus" ;
          script:contourCount ?contours .
  FILTER (?contours > 7)
}
ORDER BY DESC(?contours)"""
        
        self.query_text.delete(1.0, tk.END)
        self.query_text.insert(tk.END, examples)

    def export_kg(self):
        """Export knowledge graph to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ttl",
            filetypes=[("Turtle files", "*.ttl"), ("RDF/XML", "*.rdf"), ("JSON-LD", "*.jsonld")],
            title="Save knowledge graph"
        )
        
        if file_path:
            try:
                format = "turtle" if file_path.endswith(".ttl") else \
                         "xml" if file_path.endswith(".rdf") else \
                         "json-ld"
                self.kg.serialize(destination=file_path, format=format)
                messagebox.showinfo("Success", f"Knowledge graph saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

    def publish_as_linked_data(self):
        """Publish KG as Linked Data with PROV-O metadata"""
        base_uri = "http://example.org/indus-script/"
        
        # Add PROV-O metadata
        dataset_uri = URIRef(base_uri + "dataset")
        self.kg.add((dataset_uri, RDF.type, PROV.Entity))
        self.kg.add((dataset_uri, DCTERMS.creator, Literal("Indus Script Researcher")))
        self.kg.add((dataset_uri, DCTERMS.created, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.kg.add((dataset_uri, DCTERMS.description, 
                    Literal("Knowledge graph of Indus script symbols and related scripts")))
        
        output_dir = filedialog.askdirectory(title="Select output directory for Linked Data")
        if not output_dir:
            return
            
        try:
            os.makedirs(os.path.join(output_dir, "data"), exist_ok=True)
            
            # Serialize in multiple formats
            formats = {
                "turtle": "knowledge_graph.ttl",
                "xml": "knowledge_graph.rdf",
                "json-ld": "knowledge_graph.jsonld"
            }
            
            for fmt, filename in formats.items():
                self.kg.serialize(
                    destination=os.path.join(output_dir, "data", filename),
                    format=fmt
                )
            
            # Generate HTML portal
            with open(os.path.join(output_dir, "index.html"), "w") as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Indus Script Linked Data</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>Indus Script Linked Data</h1>
    <p>This is a FAIR dataset containing {len(self.kg)} triples about Indus script symbols.</p>
    <h2>Downloads</h2>
    <ul>
        <li><a href="data/knowledge_graph.ttl">Turtle format</a></li>
        <li><a href="data/knowledge_graph.rdf">RDF/XML format</a></li>
        <li><a href="data/knowledge_graph.jsonld">JSON-LD format</a></li>
    </ul>
    <h2>Statistics</h2>
    <ul>
        <li>Scripts: {len(list(self.kg.subjects(RDF.type, self.ns.Script)))}</li>
        <li>Symbols: {len(list(self.kg.subjects(RDF.type, self.ns.Symbol)))}</li>
    </ul>
</body>
</html>""")
            
            messagebox.showinfo("Success", f"Linked Data published to {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Publication failed: {str(e)}")

    def generate_void_description(self):
        """Generate VoID description of the dataset"""
        void = Namespace("http://rdfs.org/ns/void#")
        dataset_uri = URIRef("http://example.org/indus-script/dataset")
        
        # Clear previous VoID data
        for s, p, o in self.kg.triples((dataset_uri, None, None)):
            self.kg.remove((s, p, o))
        
        # Add VoID metadata
        self.kg.add((dataset_uri, RDF.type, void.Dataset))
        self.kg.add((dataset_uri, void.sparqlEndpoint, URIRef("http://example.org/sparql")))
        self.kg.add((dataset_uri, void.triples, Literal(len(self.kg))))
        self.kg.add((dataset_uri, void.entities, Literal(
            len(list(self.kg.subjects(RDF.type, self.ns.Script))) +
            len(list(self.kg.subjects(RDF.type, self.ns.Symbol)))
        )))
        
        # Add class partitions
        for cls in [self.ns.Script, self.ns.Symbol, self.ns.ScriptFamily]:
            partition_uri = URIRef(str(cls) + "_partition")
            self.kg.add((dataset_uri, void.classPartition, partition_uri))
            self.kg.add((partition_uri, void.cls, cls))
            self.kg.add((partition_uri, void.entities, 
                        Literal(len(list(self.kg.subjects(RDF.type, cls))))))
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ttl",
            filetypes=[("Turtle files", "*.ttl")],
            title="Save VoID description"
        )
        
        if file_path:
            try:
                self.kg.serialize(destination=file_path, format='turtle')
                messagebox.showinfo("Success", f"VoID description saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save VoID: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SemanticScriptAnalyzer(root)
    root.mainloop()
