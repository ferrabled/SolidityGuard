from antlr4 import *
from detectors.language.SolidityParser import SolidityParser
from detectors.language.SolidityLexer import SolidityLexer
from detectors.language.SolidityVisitor import SolidityVisitor
from detectors import reentrancy, statement_checker, uncheckedCall, selfdestruct, versions, integer, timestamp, denialOfService, require, dashboard
from utils import report, front, openAI
import subprocess
import os
import time
import threading

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
    contractPath, chatbot = front.main()
    #contractPath = "./contracts/all.sol"
    #chatbot = False
    if(contractPath == None):
        return

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

    def reentrancy_visitor():
        visitor = reentrancy.SolidityCallVisitor()
        visitor.visit(tree)

    def unchecked_call_visitor():
        visitor = uncheckedCall.SolidityCallVisitor()
        visitor.visit(tree)

    def selfdestruct_visitor():
        visitor = selfdestruct.SolidityCallVisitor()
        visitor.visit(tree)

    def versions_visitor():
        visitor = versions.SolidityCallVisitor()
        visitor.visit(tree)

    def integer_visitor():
        visitor = integer.SolidityCallVisitor()
        visitor.visit(tree)

    def timestamp_visitor():
        visitor = timestamp.SolidityCallVisitor()
        visitor.visit(tree)
    

    def statement_checker_visitor():
        visitor = statement_checker.SolidityCallVisitor()
        visitor.visit(tree)

    def denial_of_service_visitor():
        visitor = denialOfService.SolidityCallVisitor()
        visitor.visit(tree)
    
    def require_visitor():
        visitor = require.SolidityCallVisitor()
        visitor.visit(tree)

    #Threading for the detectors
    threading.Thread(target=reentrancy_visitor).start()
    threading.Thread(target=unchecked_call_visitor).start()
    threading.Thread(target=selfdestruct_visitor).start()
    threading.Thread(target=versions_visitor).start()
    threading.Thread(target=integer_visitor).start()
    threading.Thread(target=timestamp_visitor).start()
    threading.Thread(target=statement_checker_visitor).start()
    threading.Thread(target=denial_of_service_visitor).start()
    threading.Thread(target=require_visitor).start()

    # Wait for the threads to finish
    while threading.active_count() > 1:
        time.sleep(0.0001)

    findings = add_findings([], reentrancy.findings)
    findings = add_findings(findings, uncheckedCall.findings)
    findings = add_findings(findings, selfdestruct.findings)
    findings = add_findings(findings, versions.findings)
    findings = add_findings(findings, integer.findings)
    findings = add_findings(findings, timestamp.findings)
    findings = add_findings(findings, statement_checker.findings)
    findings = add_findings(findings, denialOfService.findings)
    require_dict = require.require_dict
    execution_time = time.time() - start_time

    print("Findings: " + str(findings))
    print("Requires: " + str(require_dict))
    print("Generating dashboard...")
    visitor = dashboard.SolidityCallVisitor()
    visitor.visit(tree)
    requires = parse_require(contractPath, require_dict)
    print(requires)
    print(len(requires))

    print("--- %s seconds ---" % (execution_time))

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
