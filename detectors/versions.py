from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser
import requests
from packaging import version


findings = []
lock_variables = []
greater = ""
less = ""

class SolidityCallVisitor(SolidityVisitor):   

    def visitPragmaValue(self, ctx: SolidityParser.PragmaValueContext):
        # petition to the Solidity webpage and retrieve the latest version
        # http request
        # compare the version from the source code with the latest version
        # if the version from the source code is lower than the latest version, then the source code is outdated
        last_version = version.parse("0.8.20")
        connection = False
        if(connection):
            try:
                last_version = requests.get('https://docs.soliditylang.org/').headers['X-RTD-Version'].replace('v', '')  
                last_version = version.parse(str(last_version))
            except Exception as e:
                print(e)
                print("Error retrieving the latest version of Solidity")
        
        if(ctx.version().getChildCount() > 1):
            for i in range(ctx.version().getChildCount()):
                if('>' in ctx.version().getChild(i).getChild(0).getText()):
                    greater = version.parse(ctx.version().getChild(i).getChild(1).getText())
                else: 
                    less =  version.parse(ctx.version().getChild(i).getChild(1).getText())
            #Compare both versions, if the gap is too big check a warning
            if(greater.major != less.major or
                greater.minor != less.minor or
                (less.micro - greater.micro > 5)):
                print("WARNING: The gap between the versions is too big")
                start, end = [ctx.start.line, ctx.start.line] 
                findings.append(['pragmaVersion', 'gap_too_big', ctx.start.line, [start, end]])
            contract_version = less
        else:
            contract_version = version.parse(ctx.version().getChild(0).getChild(1).getText())
        
        if(last_version > contract_version):
            start, end = [ctx.start.line, ctx.start.line] 
            if(last_version.major > contract_version.major):
                print("Major version outdated")
                findings.append(['pragmaVersion', 'major_outdated', ctx.start.line, [start, end]])
            elif(last_version.minor > contract_version.minor) :
                print("Minor version outdated")
                findings.append(['pragmaVersion', 'minor_outdated', ctx.start.line, [start, end]])            
            elif(last_version.micro - contract_version.micro > 7): 
                print("Micro version outdated")
                findings.append(['pragmaVersion', 'micro_outdated', ctx.start.line, [start, end]])
        return super().visitPragmaValue(ctx)
