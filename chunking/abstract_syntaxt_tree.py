import tree_sitter_python as tspython
from tree_sitter import Language, Parser

#initialize the python language
PY_LANGUAGE = Language(tspython.language())

#initialize the parser with the python language
parser = Parser(PY_LANGUAGE)

# Code to parse
code = """
def extract_chunks(node, source_bytes, chunks=None):
    if chunks is None:
        chunks = []

    if node.type in CHUNK_NODE_TYPES:
        chunk_text = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
        chunks.append({
            "type": node.type,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "text": chunk_text,
        })
        return chunks  # don't descend further into this subtree

    for child in node.children:
        extract_chunks(child, source_bytes, chunks)

    return chunks
"""

# Parse
tree = parser.parse(bytes(code, "utf8"))


# #traversing the tree manually by accessing the root node and its children
# root_node = tree.root_node
# print(f"Root node type: {root_node.type}")  # Output: module
# function_node = root_node.children[0]
# print(f"First child type: {function_node.type} \n")  # Output: function_definition




#using the walk method to traverse the tree
# cursor = tree.walk()
# print(f"Starting node: {cursor.node.type}")  # Output: module
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


# print(f"Current node: {cursor.node.type}") # Output: identifier
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