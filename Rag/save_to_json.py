import json
from chunks import create_chunks

chunks_data = create_chunks("app.py")

with open(".\\Rag\\JSON\\chunks.json", "w") as json_file:
    json.dump([chunk.__dict__ for chunk in chunks_data], json_file, indent=4)