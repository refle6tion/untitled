from dataclasses import dataclass
from Lexer import lexer

@dataclass
class Chunk:
    id:str
    name:str
    code:str
    metadata:dict
    
dependency_graph, src_metadata, entities = lexer("app.py")

chunks = []
for entity in entities:
    chunk = Chunk(
        id=f"{src_metadata.file_path}_{entity.start_line}-{entity.end_line}",
        name=entity.name,
        code=entity.code,
        metadata={
            "byte_range": entity.byte_range,
            "start_line": entity.start_line,
            "end_line": entity.end_line,
            "parent": entity.parent,
            "depth": entity.depth
        }
    )
    chunks.append(chunk)

print("Chunks:")
for chunk in chunks:
    print(f"ID: {chunk.id}, Name: {chunk.name}, Start Line: {chunk.metadata['start_line']}, End Line: {chunk.metadata['end_line']}, Parent: {chunk.metadata['parent']}, Depth: {chunk.metadata['depth']}")