from antlr4 import *
from detectors.language.SolidityParser import SolidityParser
from detectors.language.SolidityLexer import SolidityLexer
from detectors.language.SolidityVisitor import SolidityVisitor
from detectors import reentrancy, statement_checker, uncheckedCall, selfdestruct, versions, integer, timestamp, denialOfService, require, dashboard
from utils import report, front, openAI
import subprocess
import os
import time

'''
TODO // TASK LIST //
    - create a dashboard on the document that retrieves the number of lines, contracts, and fucntions analyzed
    - ✅ - all detectors -> get the line of the function start and end
    - ✅ - contract -> retrieve the vulnerable function, from the file [start:end], and send it to openAI
    - check for different contracts, rather in the same file or in different files, be able to attach 
    - ✅ - create frontend to upload the desired smart contract
    - ⌛ - create a package to install and run everythinh, executable python

    - DETECTORS TASKS:
        - selfdestruct  -> in private function check if it's being called by another function on the contract
'''

'''
TODO LIST OF DETECTORS:  ========== ✅🟢 10 / 10 ✅🟢 ==========
    - Vulnerabilities:
        - ✅ - use of tx.origin()
        - ✅ - Denial of service -> search for for or while loops [move from a push model to a pull model (withdrawal pattern)]
        - ✅ - Integer overflow and underflow -> Check that the solidity version is >= 0.8.0 or warn if it uses unchecked { ... }
        - ✅ - Timestamp dependence -> It is non deterministic, therefore it is not recommended to use it. check for block.timestamp and block.number; block.now is deprecated
    
    - Warnings: (versions.py)
        - ✅ - Version Warning -> warn the user if there's a newer version of the compiler
        - ✅ - Locking pragmas -> warn the user if it's using a wide range of versions or not locked to a specific version of the compiler 
        
    - Advices:
        - ✅ - Don't use transfer() or send() -> use call{ ... }( ... ) instead [consesys]
        - ✅ - DelegateCall advise to not delegate to untrusted conde
        - ✅ - Modifiers -> use modifiers to avoid code repetition, check if a require is being used three or more times, in the contract       

    - ALREADY DONE:
        - ✅ - Reentrancy -> check for the use of call{ ... }( ... ) and warn the user
        - ✅ - Selfdestruct
        - ✅ - UncheckedCall -> Non checking the boolean return value of call{ ... }( ... )

        
    - CANT BE MADE:
        - ❌ - Function with the same name as the contract (deprecated constructor)
        - Integer division -> All integer division rounds down to the nearest integer. If you need more precision, consider using a multiplier, or store both the numerator and denominator.
        - DelegateCall() ==> Not possible to detect if it's being called to an untrusted contract, or if it's changing the state of the contract


    - DOCUMENTATION:
        - Recommend to comment the code with the natspec format
        - Recommend to use EMITS in the events
        - Upgradeability of the contract -> speak about the proxy pattern
        - Recommend security patterns: -> Pull over push, emergency stop        
'''

def add_findings(findings, f):
    # Retrieve the recommendations from the detectors
    for find in f:
        findings.append(find)
    return findings


def get_recommendations(contractPath, findings, codefunction, chatbot):
    recommendations = []
    for find in findings:
        start, end = find[3][0], find[3][1]
        with open(contractPath, "r") as f:
            function = f.readlines()[start-1:end]
            codefunction.append(''.join(function))
        if(chatbot):
            recommendations.append(openAI.get_vulnerability_recommendation(function, find))
    if not chatbot:
        recommendations = None
    print(recommendations)
    return recommendations, codefunction

def parse_require(contractPath, require):
    requires = []
    for value in require.values():
        if(len(value) >= 3):
            print("There's a require appearing 3 or more times")
            with open(contractPath, "r") as f:
                line = f.readlines()[value[0]-1]
            requires.append([line, value])    
    return requires

def main():
    # TODO: DELETE VARIABLES
    contractPath, chatbot = front.main()
    contractPath = "./contracts/nonvuln_dos.sol"
    chatbot = False

    start_time = time.time()
    with open(contractPath, "r") as file:   
        input_code = file.read()

    # Create a lexer and parser for Solidity
    input_stream = InputStream(input_code)
    lexer = SolidityLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = SolidityParser(token_stream)

    # Generate the abstract syntax tree (AST)
    tree = parser.sourceUnit()

    visitor = reentrancy.SolidityCallVisitor()
    visitor.visit(tree)
    findings = add_findings([], reentrancy.findings)

    visitor = uncheckedCall.SolidityCallVisitor()
    visitor.visit(tree)
    findings = add_findings(findings, uncheckedCall.findings)

    visitor = selfdestruct.SolidityCallVisitor()
    visitor.visit(tree)
    findings = add_findings(findings, selfdestruct.findings)

    visitor = versions.SolidityCallVisitor()
    visitor.visit(tree)
    findings = add_findings(findings, versions.findings)

    visitor = integer.SolidityCallVisitor()
    visitor.visit(tree)
    findings = add_findings(findings, integer.findings)

    visitor = timestamp.SolidityCallVisitor()
    visitor.visit(tree)
    findings = add_findings(findings, timestamp.findings)

    visitor = statement_checker.SolidityCallVisitor()
    visitor.visit(tree)
    findings = add_findings(findings, statement_checker.findings)

    visitor = denialOfService.SolidityCallVisitor()
    visitor.visit(tree)
    findings = add_findings(findings, denialOfService.findings)
    
    visitor = require.SolidityCallVisitor()
    visitor.visit(tree)
    require_dict = require.require_dict
    
    print("Findings: " + str(findings))
    print("Requires: " + str(require_dict))

    print("Generating dashboard...")
    visitor = dashboard.SolidityCallVisitor()
    visitor.visit(tree)
    

    requires = parse_require(contractPath, require_dict)
    print(requires)
    print(len(requires))
    print("--- %s seconds ---" % (time.time() - start_time))


    # Get dashboard data 
    data = dashboard.get_data()
    data.append([len(require_dict), len(requires)])
    data.append(len(findings))
    print("ALL DATA: " + str(data))
    # Data = [lines, contracts, functions, emits, [requires, requires_repeated], findings
    
    recommendations, fun = get_recommendations(contractPath, findings, [], chatbot)
    report.generate_report(findings, recommendations, fun, requires, data)
    print(len(findings))
    print("Opening report...")

    url = "report.html"
    try: # should work on Windows
        os.startfile(url)
    except AttributeError:
        try: # should work on MacOS and most linux versions
            subprocess.call(['open', url])
        except:
            print('Could not open URL')    

if __name__ == "__main__":
    main()
