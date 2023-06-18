from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser
from detectors.AST_utils import get_function_start_end, TerminalNode

findings = []

# Self destruct function removes all the bytecode from the contract address
# After the self destruct, the contract address is no longer valid
# An attacker can create a selfdestructfunction(target) in order to 
# destroy the contract and send its balance to the target address

# This vulnerability can be due to letting the function public or not 
# checking the sender address with a modifier as onlyOwner.

class SolidityCallVisitor(SolidityVisitor):

    def visitFunctionDefinition(self, ctx):
        # Check if the function contains a 'self_destruct' node
        self_destruct_node = self.find_selfdestruct_node(ctx)

        if self_destruct_node is not None:
            selfdestruct_line = self_destruct_node.getPayload().line    

            # Check whether the function has a onlyOwner modifier
            # This modifier checks if the sender address is the same as the owner address
            # If the function does not have a modifier, it is considered as a vulnerability
            
            if (ctx.modifierList().getChild(0).getText() == "private"):
                # Even if the function is private, it can be called by another function on the contract
                # Therefore, it is considered as a vulnerability if not treated properly
                
                # TODO check if the function is being called by another function on the contract 
                start, end = get_function_start_end(self_destruct_node) 
                findings.append(['selfdestruct', 'private', selfdestruct_line, [start, end]])
                print("it's a private function")
                return super().visitFunctionDefinition(ctx)


            for value in ctx.modifierList().modifierInvocation():                
                if value.getText() == 'onlyOwner':
                    print("OnlyOwner modifier found")
                    start, end = get_function_start_end(self_destruct_node) 
                    findings.append(['selfdestruct', 'onlyOwner', selfdestruct_line, [start, end]])
                    return super().visitFunctionDefinition(ctx)
            
            # Check for a require statement in the function before the selfdestruct
            # If the require statement is not met, the selfdestruct will not be executed
            # Therefore, it is not considered as a vulnerability
            require = self.find_require_node(ctx.block(), selfdestruct_line)
            if require is not None:
                expression = require.expression().functionCallArguments().getText()
                if 'owner' in str(expression):
                    start, end = get_function_start_end(self_destruct_node) 
                    findings.append(['selfdestruct', 'require owner', selfdestruct_line, [start, end]])
                    return super().visitFunctionDefinition(ctx) 
                
                else:
                    start, end = get_function_start_end(self_destruct_node) 
                    findings.append(['selfdestruct', 'vulnerable', selfdestruct_line, [start, end]])
                    return super().visitFunctionDefinition(ctx)

            else:
                if(selfdestruct_line not in findings):
                    start, end = get_function_start_end(self_destruct_node) 
                    findings.append(['selfdestruct', 'vulnerable', selfdestruct_line, [start, end]])
                    return super().visitFunctionDefinition(ctx)            
        return super().visitFunctionDefinition(ctx)


    def find_selfdestruct_node(self, ctx:SolidityParser.FunctionDefinitionContext):
        # Auxiliar function to find the 'selfdestruct' node in the current context
        if isinstance(ctx, TerminalNode):
            if ctx.getText() == 'selfdestruct':
                return ctx
            return None
        try:
            for child in ctx.children:
                call_node = self.find_selfdestruct_node(child)
                if call_node is not None:
                    return call_node
        except :
            return None
        return None

    def find_require_node(self, ctx:SolidityParser.BlockContext, selfdestruct_line):

        
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

        # Auxiliar function to find the 'require' node in the current context
        if isinstance(ctx, TerminalNode):

            if ctx.getText() == 'require' and selfdestruct_line > ctx.getPayload().line:
                expression_statement = find_nearest_ancestor_of_type(ctx, SolidityParser.ExpressionStatementContext)
                return expression_statement
            return None
        try:
            for child in ctx.children:
                call_node = self.find_require_node(child, selfdestruct_line)
                if call_node is not None:
                    return call_node
        except:
            return None
        return None