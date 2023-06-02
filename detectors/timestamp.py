from detectors.AST_utils import get_function_start_end
from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser
from antlr4 import TerminalNode

findings = []

class SolidityCallVisitor(SolidityVisitor):
    
    def find_child_node_contains(self, ctx, text, nodetype):
        # Auxiliar function to find the text node in the current context
        if isinstance(ctx, TerminalNode):
            return None
        if (ctx.__class__.__name__ == nodetype.__name__ and text in ctx.getText()):
            return ctx
        for child in ctx.children:
            call_node = self.find_child_node_contains(child, text, nodetype)
            if call_node is not None:
                return call_node
        return None


    def visitBlock(self, ctx: SolidityParser.BlockContext):
        if ("block.timestamp" in ctx.getText() 
            or "block.now" in ctx.getText()
            or "block.number" in ctx.getText()):
            block = self.used_block(ctx.getText())
            print(block, " found")
            block_node = self.find_child_node_contains(ctx, block, SolidityParser.ExpressionContext)
            start, end = get_function_start_end(ctx)
            findings.append(['timestamp', block, block_node.start.line, [start, end]])
        return super().visitExpression(ctx)
    

    def used_block(self, text):
        if "block.timestamp" in text:
            return "block.timestamp"
        elif "block.number" in text:
            return "block.number"
        elif "block.now" in text:
            return "block.now"