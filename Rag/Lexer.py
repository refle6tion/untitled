from Visitor import traverse, file_metadata, scope_stack, Entity_depth
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


def lexer(file_path: str):
    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)

    entities = []
    
    # with open(file_path) as f:
    #     code = f.read()

    code = """def greet():
    print("Hello")


class A:
    def foo(self):
        greet()


class B:
    def bar(self):
        a = A()
        a.foo()


def main():
    b = B()
    b.bar()


main()"""
            
    tree = parser.parse(code.encode())
    cursor = tree.walk()
    
    traverse(cursor, scope_stack, entities)
    src_metadata = file_metadata(file_path)
    
    return src_metadata, entities


src_metadata, entities = lexer("app.py")
for entity in entities:
    indent = "    " * entity.depth
    print(f"{indent}Entity: {entity}\n ")

