from Visitor import traverse, file_metadata, scope_stack, Entity_depth
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


def lexer(file_path: str):
    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)

    dependency_graph = []
    entities = []
    
    with open(file_path) as f:
        code = f.read()

    tree = parser.parse(code.encode())
    cursor = tree.walk()
    
    traverse(cursor, scope_stack, entities)
    src_metadata = file_metadata(file_path)

    for entity in entities:
        dependency_graph.append(Entity_depth(name=entity.name, depth=entity.depth, parent=entity.parent))
    
    return dependency_graph, src_metadata, entities


dependency_graph, src_metadata, entities = lexer("app.py")

for entity in dependency_graph:
    print(f"Entity: Name: {entity.name}\n, Depth: {entity.depth}, Parent: {entity.parent}\n")