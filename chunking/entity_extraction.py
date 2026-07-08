from dataclasses import dataclass
from marshal import dump
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

code = """ 
import os
from dataclasses import dataclass

P   I = 3.14


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

CONTROL_FLOW_NODES = {"if_statement", "elif_clause", "else_clause",
    "for_statement", "while_statement",
    "try_statement", "except_clause", "finally_clause",
    "with_statement", "match_statement", "case_clause",}


def get_code(cursor) -> str:
    for child in cursor.node.children:
        if child.type == "block":
            return child.text.decode()
    return None




def get_decorator_identifier(cursor) -> str:
    reached_root = False
    depth = 0
    if cursor.node.type == "decorator":
        while not reached_root:
            if cursor.node.type == "identifier":
                identifier = cursor.node.text.decode()
                while depth > 0:
                    cursor.goto_parent()
                    depth -= 1
                return identifier
            
            if cursor.goto_first_child() :
                depth += 1
                continue            
            
            if cursor.goto_next_sibling() :
                continue
            
            while True:
                if cursor.node.type == "decorator":
                    reached_root = True
                    break
                else:
                    cursor.goto_parent()
                    depth -= 1
                    
                if cursor.goto_next_sibling() :
                    break
                


def get_headder(cursor)-> str:
    """
    Get the header of a node, which is the first line of code that defines the entity.
    """
    headders =[]
    for child in cursor.node.children:
        if child.type != "block":
            headders.append(child.text.decode())
    
    headder = " ".join(headders)
    return headder

tree = parser.parse(code.encode())
cursor = tree.walk()
scope_stack = [ScopeFrame("module", None)]


def visit_function_definition(scope_stack, cursor):
    print("FUNCTION")
    print(get_headder(cursor))
    print("code: \n", get_code(cursor))
    print("parent =", scope_stack[-1].name, "\n")
    
def visit_class_definition(scope_stack, cursor):
    print("CLASS")
    print(get_headder(cursor))
    print("code: \n", get_code(cursor))
    print("parent =", scope_stack[-1].name, "\n")
    
def visit_decorated_function(scope_stack, cursor):
    print("DECORATED FUNCTION")
    print(get_headder(cursor))
    print("code: \n", get_code(cursor))
    print("parent =", scope_stack[-1].name, "\n")    

def visit_decorator(scope_stack, cursor):
    print("DECCORATOR")
    print(f"@{get_decorator_identifier(cursor)}")
    print("code: \n", get_code(cursor))
    print("parent =", scope_stack[-1].name, "\n")

def visit_import_statement(scope_stack, cursor):
    print("IMPORT")
    print(get_headder(cursor))
    print("code: \n", get_code(cursor))   
    print("parent =", scope_stack[-1].name, "\n")
    
def visit_import_from_statement(scope_stack, cursor):
    print("IMPORT FROM")
    print(get_headder(cursor))
    print("code: \n", get_code(cursor)) 
    print("parent =", scope_stack[-1].name, "\n") 
    
def visit_variable_declaration(scope_stack, cursor):
    if scope_stack[-1].name == None:
        print("VARIABLE DECLARATION")
        print(cursor.node.text.decode(),"\n")

def visit_control_flow(scope_stack, cursor):
    if scope_stack[-1].name == None:
        print("CONTROL FLOW")
        print(get_headder(cursor))
        print("code: \n", get_code(cursor)) 
        print("parent =", scope_stack[-1].name, "\n")

VISITOR = {
    "function_definition": visit_function_definition,
    "class_definition": visit_class_definition,
    "decorated_function": visit_decorated_function,
    "decorator": visit_decorator,
    "import_statement": visit_import_statement,
    "import_from_statement": visit_import_from_statement,
    "expression_statement": visit_variable_declaration,
    "if_statement": visit_control_flow,
    "elif_clause": visit_control_flow,
    "else_clause": visit_control_flow,
    "for_statement": visit_control_flow,
    "while_statement": visit_control_flow,
    "try_statement": visit_control_flow,
    "except_clause": visit_control_flow,
    "finally_clause": visit_control_flow,
    "with_statement": visit_control_flow,
    "match_statement": visit_control_flow,
    "case_clause": visit_control_flow
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
            scope_stack.append(ScopeFrame(ScopeFrame_kind, get_headder(cursor)))

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
