from dataclasses import dataclass
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from pathlib import Path

@dataclass
class File_Metadata:
    file_path: Path
    file_name: str
    directory: str

@dataclass
class Entity_depth:
    name: str
    depth: int
    parent: str | None = None

@dataclass
class Entity:
    type: str
    name: str
    param: str | None
    code: str
    start_line: int
    end_line: int
    parent: str | None
    depth: int = 0


@dataclass
class ScopeFrame:
    kind: str          
    name: str | None 

scope_stack = [ScopeFrame("module", None)]


CONTROL_FLOW_NODES = {"if_statement", "elif_clause", "else_clause",
    "for_statement", "while_statement",
    "try_statement", "except_clause", "finally_clause",
    "with_statement", "match_statement", "case_clause",}

def get_code(cursor) -> str:
    for child in cursor.node.children:
        if child.type == "block":
            return child.text.decode()
    return None

def get_params(cursor) -> str:
    for child in cursor.node.children:
        if child.type == "parameters":
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


def visit_function_definition(scope_stack, cursor):
    entity = Entity(
        type="function",
        name=get_headder(cursor),
        param=get_params(cursor),
        code=get_code(cursor) if get_code(cursor) is not None  else "",
        start_line=cursor.node.start_point[0] + 1,
        end_line=cursor.node.end_point[0] + 1,
        parent=scope_stack[-1].name if scope_stack[-1].name is not None else "" ,
        depth=cursor.depth,
    )
    return entity

def visit_class_definition(scope_stack, cursor):
    entity = Entity(
        type="class",
        name=get_headder(cursor),
        param=get_params(cursor),
        code=get_code(cursor) if get_code(cursor) is not None  else "",
        start_line=cursor.node.start_point[0] + 1,
        end_line=cursor.node.end_point[0] + 1,
        parent=scope_stack[-1].name if scope_stack[-1].name is not None else "",
        depth=cursor.depth,
    )
    return entity
    
def visit_decorated_function(scope_stack, cursor):
    entity = Entity(
        type="decorated_function",
        name=get_headder(cursor),
        param=get_params(cursor),
        code=get_code(cursor) if get_code(cursor) is not None  else "",
        start_line=cursor.node.start_point[0] + 1,
        end_line=cursor.node.end_point[0] + 1,
        parent=scope_stack[-1].name if scope_stack[-1].name is not None else "",
        depth=cursor.depth,
    )
    return entity    

def visit_decorator(scope_stack, cursor):
    entity = Entity(
        type="decorator",
        name=get_decorator_identifier(cursor),
        param="None",
        code=get_code(cursor) if get_code(cursor) is not None  else "",
        start_line=cursor.node.start_point[0] + 1,
        end_line=cursor.node.end_point[0] + 1,
        parent=scope_stack[-1].name if scope_stack[-1].name is not None else "",
        depth=cursor.depth
    )
    return entity

def visit_import_statement(scope_stack, cursor):
    entity = Entity(
        type="import_statement",
        name=get_headder(cursor),
        param="None",
        code=get_code(cursor) if get_code(cursor) is not None  else "",
        start_line=cursor.node.start_point[0] + 1,
        end_line=cursor.node.end_point[0] + 1,
        parent=scope_stack[-1].name if scope_stack[-1].name is not None else "",
        depth=cursor.depth
    )
    return entity

def visit_import_from_statement(scope_stack, cursor):
    entity = Entity(
        type="import_from_statement",
        name=get_headder(cursor),
        param="None",
        code=get_code(cursor) if get_code(cursor) is not None  else "",
        start_line=cursor.node.start_point[0] + 1,
        end_line=cursor.node.end_point[0] + 1,
        parent=scope_stack[-1].name if scope_stack[-1].name is not None else "",
        depth=cursor.depth
    )
    return entity

def visit_variable_declaration(scope_stack, cursor):
    if scope_stack[-1].kind == "module":
        entity = Entity(
            type="variable_declaration",
            name=get_headder(cursor),
            param="None",
            code=get_code(cursor) if get_code(cursor) is not None  else "",
            start_line=cursor.node.start_point[0] + 1,
            end_line=cursor.node.end_point[0] + 1,
            parent=scope_stack[-1].name if scope_stack[-1].name is not None else "",
            depth=cursor.depth
        )
        return entity

def visit_control_flow(scope_stack, cursor):
    if scope_stack[-1].kind == "module":
        entity = Entity(
            type="control_flow",
            name=get_headder(cursor),
            param="None",
            code=get_code(cursor) if get_code(cursor) is not None  else "",
            start_line=cursor.node.start_point[0] + 1,
            end_line=cursor.node.end_point[0] + 1,
            parent=scope_stack[-1].name if scope_stack[-1].name is not None else "",
            depth=cursor.depth
        )
        return entity

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

def file_metadata(file_path: str) -> File_Metadata:
    path = Path(file_path)
    return File_Metadata(
        file_path=path,
        file_name=path.name,
        directory=str(path.parent)
    )

def traverse(cursor, scope_stack, entities):
    node = cursor.node

    visitor = VISITOR.get(node.type)
    if visitor:
        entity = visitor(scope_stack, cursor)
        if entity is not None:
            entities.append(entity)

        ScopeFrame_kind = SCOPE.get(node.type)
        if ScopeFrame_kind:
            scope_stack.append(ScopeFrame(ScopeFrame_kind, get_headder(cursor)))

        if cursor.goto_first_child():
            while True:
                traverse(cursor, scope_stack, entities)

                if not cursor.goto_next_sibling():
                    break

            cursor.goto_parent()
        
        if ScopeFrame_kind:
            scope_stack.pop()
        return
    
    if cursor.goto_first_child():
        while True:
            traverse(cursor, scope_stack, entities)

            if not cursor.goto_next_sibling():
                break

        cursor.goto_parent()

