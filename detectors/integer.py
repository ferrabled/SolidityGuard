from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser
from antlr4 import *
from packaging import version
from detectors.AST_utils import *


# - Integer overflow and underflow -> Check that the solidity version is >= 0.8.0 OR use SafeMath if uses unchecked { ... } it's vulnerable
findings = []

class SolidityCallVisitor(SolidityVisitor):   
    

    def visitPragmaValue(self, ctx: SolidityParser.PragmaValueContext):
        if(ctx.version().getChildCount() > 1):
            for i in range(ctx.version().getChildCount()):
                if('>' in ctx.version().getChild(i).getChild(0).getText()):
                    greater = version.parse(ctx.version().getChild(i).getChild(1).getText())
                else: 
                    less =  version.parse(ctx.version().getChild(i).getChild(1).getText())
            contract_version = less
        else:
            contract_version = version.parse(ctx.version().getChild(0).getChild(1).getText())
        
        if(contract_version < version.parse("0.8.0")):
            findings.append(['integer', 'outdated', ctx.start.line, [ctx.start.line, ctx.start.line]])

        return super().visitPragmaValue(ctx)
    

    
    def visitUncheckedStatement(self, ctx: SolidityParser.UncheckedStatementContext):
        start, end = get_function_start_end(ctx) 
        findings.append(['integer', 'unchecked', ctx.start.line ,[start, end]])
        return super().visitUncheckedStatement(ctx)
    

    
    