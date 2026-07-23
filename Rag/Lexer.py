from Visitor import traverse, file_metadata, scope_stack, Entity_depth
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


def lexer(file_path: str):
    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)

    entities = []
    
    # with open(file_path) as f:
    #     code = f.read()

    code = """import os
from dataclasses import dataclass

PI = 3.14


def log(func):
    return func


@dataclass
class Point:
    x: int
    y: int


@log
class User:
    role = "admin"

    def __init__(self, name):
        self.name = name

    @staticmethod
    def greet():
        print("Hello")

    def login(self):
        token = "abc"

        if token:
            print("Logged in")
        else:
            print("Failed")

        return token


@log
def helper(x: int) -> int:
    return x * 2


if __name__ == "__main__":
    user = User("Alice")
    helper(10)"""
            
    tree = parser.parse(code.encode())
    cursor = tree.walk()
    
    traverse(cursor, scope_stack, entities)
    src_metadata = file_metadata(file_path)
    
    return src_metadata, entities


src_metadata, entities = lexer("app.py")
for entity in entities:
    indent = "    " * entity.depth
    print(f"{indent}Entity: {entity}\n ")

