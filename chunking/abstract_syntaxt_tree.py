import tree_sitter_python as tspython
from tree_sitter import Language, Parser

#initialize the python language
PY_LANGUAGE = Language(tspython.language())

#initialize the parser with the python language
parser = Parser(PY_LANGUAGE)

# # Code to parse a complete python file and get the abstract syntax tree
# with open("app.py") as f:
#     code = f.read()

#code to parse a small string of code 
code = """ 
import os
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

# Parse
tree = parser.parse(bytes(code, "utf8"))


# #traversing the tree manually by accessing the root node and its children
# root_node = tree.root_node
# print(f"Root node type: {root_node.type}")  # Output: module
# function_node = root_node.children[0]
# print(f"First child type: {function_node.type} \n")  # Output: function_definition


##code to figure out the structure of the tree and its nodes
# cursor = tree.walk()
# current_node = cursor.node
# cursor.goto_first_child()
# current_node_function_name = cursor.node.children[0].text.decode()
# current_node_name = cursor.node.named_children[0].text.decode()
# cursor.goto_last_child()
# current_node_last_child = cursor.node.type
# current_node_first_child = cursor.node.children[0].type
# cursor.goto_first_child()
# current_node_first_child_first_child = cursor.node.children[0].text.decode()
# current_node_first_child_first_child_type = cursor.node.named_children[0].text.decode()
# print(current_node_function_name, current_node_name, current_node_last_child, current_node_first_child, current_node_first_child_first_child, current_node_first_child_first_child_type)




# #using the walk method to traverse the tree
# cursor = tree.walk()
# print(f"Starting node: {cursor.node.type} , {cursor.depth} ")  # Output: module
# print(f"First child: {cursor.goto_first_child()}") # returns true and moves to function_definition node
# print(f"First childs first child: {cursor.goto_first_child()}") # .returns true and moves to the def node
# print(f"first childs first childs sibblings : {cursor.goto_next_sibling()}") #returns true and moves to the identifer node
# print(f"first childs first childs sibblings : {cursor.goto_next_sibling()}") #returns true and moves to the parameters node
# print(f"first childs first childs sibblings : {cursor.goto_next_sibling()}") #returns true and moves to the : node
# print(f"first childs first childs sibblings : {cursor.goto_next_sibling()}") #returns true and moves to the block node
# print(f"first childs first childs last sibblings first child: {cursor.goto_first_child()}") #returns true and moves to the expression_statement node
# print(f"first childs first childs last sibblings first child first child: {cursor.goto_first_child()}") #returns true and moves to the call node
# print(f"first childs first childs last sibblings first child first child first child: {cursor.goto_first_child()}") #returns true and moves to the identifier node
# print(f"first childs first childs last sibblings first child first child first child next sibling: {cursor.goto_next_sibling()}") #returns true and moves to the argument_list node
# print(f"Current node: {cursor.node.type} , {cursor.depth} ") # Output: identifier
# print(f"Current node text: {cursor.node.text.decode('utf-8')}") # Output: greet


def dfs_traverse(tree):
    cursor = tree.walk()
    depth = 0
    reached_root = False

    while not reached_root:
        node = cursor.node
        print("  " * depth + f"{node.type}" + 
              (f" -> {node.text.decode('utf-8')!r}" if node.child_count == 0 else ""))

        # 1. Try to go down
        if cursor.goto_first_child():
            depth += 1
            continue

        # 2. No children -> try next sibling
        if cursor.goto_next_sibling():
            continue

        # 3. No sibling -> climb back up until we find one, or hit root
        while True:
            if not cursor.goto_parent():
                reached_root = True
                break
            depth -= 1
            if cursor.goto_next_sibling():
                break
    dfs_traverse(tree)