from dataclasses import dataclass
from marshal import dump
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

code = """ 
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



@dataclass
class Entity:
    type: str
    name: str
    param: str | None
    code: str
    byte_range: tuple[int, int]
    start_line: int
    end_line: int
    parent: str | None


@dataclass
class ScopeFrame:
    kind: str          
    name: str | None 

def get_headder(node)-> str:
    """
    Get the header of a node, which is the first line of code that defines the entity.
    """
    headders =[]
    for child in node.children[:-1]:  # Exclude the last child (the body)
        headders.append(child.text.decode())
    
    headder = " ".join(headders)
    return headder



tree = parser.parse(code.encode())
cursor = tree.walk()
scope_stack = [ScopeFrame("module", None)]


def visit_function_definition(scope_stack, cursor):
    print("FUNCTION")
    print(get_headder(cursor.node))
    print("parent =", scope_stack[-1].name, "\n")
    
def visit_class_definition(scope_stack, cursor):
    print("CLASS")
    print(get_headder(cursor.node))
    print("parent =", scope_stack[-1].name, "\n")
    
def visit_decorated_function(scope_stack, cursor):
    print("DECORATED FUNCTION")
    print(get_headder(cursor.node))
    print("parent =", scope_stack[-1].name, "\n")    

def visit_decorator(scope_stack, cursor):
    print("DECCORATOR")
    print(get_headder(cursor.node))
    print("parent =", scope_stack[-1].name, "\n")

def visit_import_statement(scope_stack, cursor):
    print("IMPORT")
    print(get_headder(cursor.node))
    print("parent =", scope_stack[-1].name, "\n")
    
def visit_import_from_statement(scope_stack, cursor):
    print("IMPORT FROM")
    print(get_headder(cursor.node))
    print("parent =", scope_stack[-1].name, "\n") 

VISITOR = {
    "function_definition": visit_function_definition,
    "class_definition": visit_class_definition,
    "decorated_function": visit_decorated_function,
    "decorator": visit_decorator,
    "import_statement": visit_import_statement,
    "import_from_statement": visit_import_from_statement
}

SCOPE = {
    "function_definition": "function",
    "class_definition": "class",
    "decorated_function": "decorated_function",
}

def traverse(cursor, scope_stack):
    node = cursor.node

    visitor = VISITOR.get(node.type)
    if visitor:
        visitor(scope_stack, cursor)
        
        ScopeFrame_kind = SCOPE.get(node.type)
        if ScopeFrame_kind:
            scope_stack.append(ScopeFrame(ScopeFrame_kind, get_headder(node)))

        if cursor.goto_first_child():
            while True:
                traverse(cursor, scope_stack)

                if not cursor.goto_next_sibling():
                    break

            cursor.goto_parent()
        
        if ScopeFrame_kind:
            scope_stack.pop()
        return
    
    if cursor.goto_first_child():
        while True:
            traverse(cursor, scope_stack)

            if not cursor.goto_next_sibling():
                break

        cursor.goto_parent()
        
        
        
traverse (cursor, scope_stack)