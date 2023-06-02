from detectors.AST_utils import get_function_start_end
from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser
from detectors.AST_utils import *

findings = []


class SolidityCallVisitor(SolidityVisitor):

    def visitFunctionDefinition(self, ctx: SolidityParser.BlockContext):
        if ("tx.origin" in ctx.getText()):
            block_node = find_child_node_contains(ctx, "tx.origin", SolidityParser.ExpressionContext)
            if(block_node is None):
                return super().visitExpression(ctx)
            start, end = get_function_start_end(ctx)
            findings.append(['tx.origin', "vulnerable", block_node.start.line, [start, end]])
        
        if ("delegatecall(" in ctx.getText()):
            block_node = find_child_node_contains(ctx, "delegatecall", SolidityParser.ExpressionContext)
            if(block_node is None):
                return super().visitExpression(ctx)
            start, end = get_function_start_end(ctx)
            findings.append(['delegatecall', "advisory", block_node.start.line, [start, end]])
        
        if ("transfer(" in ctx.getText()):
            block_node = find_child_node_contains(ctx, "transfer", SolidityParser.ExpressionContext)
            if(block_node is None):
                return super().visitExpression(ctx)
            start, end = get_function_start_end(ctx)
            findings.append(['transfer', "advisory", block_node.start.line, [start, end]])
        
        if ("send(" in ctx.getText()):
            block_node = find_child_node_contains(ctx, "send", SolidityParser.ExpressionContext)
            if(block_node is None):
                return super().visitExpression(ctx)
            start, end = get_function_start_end(ctx)
            findings.append(['send', "advisory", block_node.start.line, [start, end]])

        return super().visitExpression(ctx)
    