from detectors.language.SolidityParser import SolidityParser
from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser

'''
    The data we want to obtain is:
    
    [General Data]
    - Number of contracts ✅
    - Number of functions ✅
    - Number of lines of code 
    
    [Detectors Data]
    - Number of findings: ✅
        - Vulnerabilities
        - Warnings
        - Advices

    [Solidity Data]
    - Number of emits ✅
    - Number of requires ✅
    - Number of requires appearing more than 3 times ✅
'''

contracts = [0]
functions = [0]
emits = [0]
lines = [0]

#Empack the data in a list
def get_data():
    data = []
    data.append(lines[0])
    data.append(contracts[0])
    data.append(functions[0])
    data.append(emits[0])
    return data



class SolidityCallVisitor(SolidityVisitor):

    
    def visitContractDefinition(self, ctx: SolidityParser.ContractDefinitionContext):
        contracts[0] = contracts[0] + 1
        # get the last line of the contract
        lines[0] = ctx.stop.line
        return super().visitContractDefinition(ctx)

    def visitFunctionDefinition(self, ctx: SolidityParser.FunctionDefinitionContext):
        functions[0] = functions[0] + 1
        return super().visitFunctionDefinition(ctx)

    def visitEmitStatement(self, ctx: SolidityParser.EmitStatementContext):
        emits[0] = emits[0] + 1
        return super().visitEmitStatement(ctx)
    