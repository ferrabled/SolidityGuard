from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser
from antlr4 import TerminalNode
from detectors.AST_utils import get_function_start_end

findings = []

class SolidityCallVisitor(SolidityVisitor):

    def visitFunctionDefinition(self, ctx):
        # Check if the function contains a 'Call' node
        call_node = self.find_call_node(ctx.block())
        if call_node is not None:
            # Check whether the function checks the return value of the call
            # If the return value fails, the function does not throw an error, 
            # it returns false, the execution continues and could led to unexpected behaviour
            call_line = call_node.getPayload().line

            # Once we've found the call node, we're going to check if
            # the function checks the return value, if it does, 
            # the node should be a variable declaration statement


            bool_node = self.find_nearest_ancestor_of_type(call_node, SolidityParser.VariableDeclarationStatementContext)
            if bool_node is None:
                start, end = get_function_start_end(call_node) 
                findings.append(['uncheckedCall', 'vulnerable', call_node.getPayload().line, [start, end]])

                return super().visitFunctionDefinition(ctx)
            else:
                #print(bool_node.getText())
                contains:bool = ('bool' in bool_node.getText() and '=' in bool_node.getText())
                print("Checked low level call found on line", str(call_line) + ", not vulnerable")
                if(not contains):
                    print("Possible unchecked call found, bool and equals not found on variableDeclarationStatement")
                    start, end = get_function_start_end(call_node)
                    findings.append(['uncheckedCall', 'nonCheck', call_node.getPayload().line, [start, end]])
                return super().visitFunctionDefinition(ctx)


    def find_nearest_ancestor_of_type(self, node, ancestor_type):
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



    def find_call_node(self, ctx:SolidityParser.BlockContext):
        # Auxiliar function to find the 'call', 'callnode', 'delegatecall' or 'send' node in the current context
        if isinstance(ctx, TerminalNode):
            if ctx.getText() == 'call' or ctx.getText() == 'callcode' or ctx.getText() == 'delegatecall' or ctx.getText() == 'send' or ctx.getText() == 'staticcall':
                return ctx
            return None
        try:
            for child in ctx.children:
                call_node = self.find_call_node(child)
                if call_node is not None:
                    return call_node
        except Exception as e:
            return None
        return None


