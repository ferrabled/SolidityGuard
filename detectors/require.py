from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser

#TODO: check if a modifier is counted as a require inside an expressionstatement


require_dict = {}
class SolidityCallVisitor(SolidityVisitor):
    def visitExpressionStatement(self, ctx: SolidityParser.ExpressionStatementContext):
        if ("require" in ctx.getText()):
            #Get the hash of the require statement
            ctx_hash = hash(ctx.expression().getText().strip())
            if(ctx_hash in require_dict):
                require_dict[ctx_hash].append(ctx.start.line)
            else:
                require_dict[ctx_hash] = [ctx.start.line]
        return super().visitExpressionStatement(ctx)
    