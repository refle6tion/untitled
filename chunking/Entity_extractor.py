from dataclasses import dataclass
from pathlib import Path
from Visitor import traverse, file_metadata, scope_stack, Entity_depth
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

file_path = "app.py"

with open(file_path) as f:
    code = f.read()

tree = parser.parse(code.encode())
cursor = tree.walk()


dependency_graph = []
entities = []
traverse(cursor, scope_stack, entities)
file_metadata = file_metadata(file_path)

print(f"File Metadata: Path: {file_metadata.file_path}, Name: {file_metadata.file_name}, Directory: {file_metadata.directory}") 

for entity in entities:
    dependency_graph.append(Entity_depth(name=entity.name, depth=entity.depth, parent=entity.parent))

for entity in dependency_graph:
    print(f"Entity: Name: {entity.name}\n, Depth: {entity.depth}, Parent: {entity.parent}\n")