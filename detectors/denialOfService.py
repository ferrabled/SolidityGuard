from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser
from detectors.AST_utils import get_function_start_end, find_child_node_contains

'''
    This detector finds denial of service vulnerabilities in Solidity smart contracts.
    It checks for the following patterns:
        - Loops without checks on the gas left
        - Loops with checks on the gas left inside require statements
    If neither of these patterns are found, the function is marked as vulnerable.
'''

findings = []
lock_variables = []

def find_expression_statement_parent(ctx):
    # Iterate the parent nodes until we find the expressionStatement parent
    # This is the parent node of the require statement, it will be checking the mutex
    parent = ctx.parentCtx
    while parent is not None:
        if parent.getRuleIndex() ==  SolidityParser.RULE_expressionStatement and 'require' in parent.getText():
            return parent
        parent = parent.parentCtx
    return None


class SolidityCallVisitor(SolidityVisitor):   
    def visitForStatement(self, ctx: SolidityParser.ForStatementContext):
        childnode = find_child_node_contains(ctx, 'gasleft', SolidityParser.ExpressionContext)
        if(childnode != None and find_expression_statement_parent(childnode) != None):
            print("Gas check found inside require")
            return super().visitForStatement(ctx)
        start, end = get_function_start_end(ctx)
        findings.append(['dos', 'for', ctx.start.line, [start, end]])
        return super().visitForStatement(ctx)
    

    def visitWhileStatement(self, ctx: SolidityParser.WhileStatementContext):
        expression_node = ctx.expression().getText() or None
        if(expression_node != None and 'gasleft' in expression_node):
            print("Gas check found")
            return super().visitWhileStatement(ctx)
        else:
            print(expression_node) 
            childnode = find_child_node_contains(ctx, 'gasleft', SolidityParser.ExpressionContext)
            if(childnode != None):
                parentstatement = find_expression_statement_parent(childnode)
                if(parentstatement != None):
                    print("Gas check found inside require")
                    return super().visitWhileStatement(ctx)
            start, end = get_function_start_end(ctx)
            findings.append(['dos', 'while', ctx.start.line, [start, end]])
        return super().visitWhileStatement(ctx)
