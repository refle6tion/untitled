from dataclasses import dataclass
from pathlib import Path
from Lexer import lexer

@dataclass
class Chunk:
    id:str
    document:str
    metadata:dict

def create_chunks(file_path: str):
    file_path = Path(file_path)
    dependency_graph, src_metadata, entities = lexer(file_path)
    chunks = []
    for entity in entities:
        chunk = Chunk(
            id=f"{src_metadata.file_path}_{entity.start_line}-{entity.end_line}",
            document=f"{entity.name} {entity.code}",
            metadata={
                "name": entity.name,
                "type": entity.type,
                "start_line": entity.start_line,
                "end_line": entity.end_line,
                "parent": entity.parent,
                "depth": entity.depth
            }
        )
        chunks.append(chunk)
    return chunks

chunks = create_chunks("app.py")
