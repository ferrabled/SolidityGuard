from .language.SolidityParser import SolidityParser
from antlr4 import TerminalNode 

def get_function_start_end(node):
    while node is not None:
        if (node.__class__.__name__ == SolidityParser.FunctionDefinitionContext.__name__):
            start = node.start.line
            end = node.stop.line
            return start, end
        node = node.parentCtx
    return None


def find_nearest_ancestor_of_type(node, ancestor_type):
    """
    Finds the nearest ancestor node of the specified type in the parse tree
    starting from the given node.
    Returns None if no ancestor of that type is found.
    """
    while node is not None:
        if (node.__class__.__name__ == ancestor_type.__name__):
            return node
        node = node.parentCtx
    return None


def find_child_node_contains(ctx, text, nodetype):
    # Auxiliar function to find the text node in the current context
    if isinstance(ctx, TerminalNode):
        return None
    if (ctx.__class__.__name__ == nodetype.__name__ and text in ctx.getText()):
        return ctx
    try:
        for child in ctx.children:
            call_node = find_child_node_contains(child, text, nodetype)
            if call_node is not None:
                return call_node
    except:
        return None
    return None