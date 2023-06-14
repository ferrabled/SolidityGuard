import json
import sys
import os

# Get the path to the JSON file
base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
# Get the path to the JSON file
json_path = os.path.join(base_path, "utils", "data.json")
json_data = json.load(open(json_path, "r"))

def generate_html(findings: list, recommendations: list, functions: list, requires: list, data: list):
    print("Generating html report")
    header = '''
        <!DOCTYPE html>
        <html>
        <head>
        <link rel="stylesheet" href="utils/style.css">
        <title>Report</title>
        </head>
        <body>
    '''
    pageheader = '''
        <div class="pageHeader">
            <div class="iconName"> <img src="icon.png" alt="Logo" width="40" height="40"> Solidity Guard </div>
            <div class="separator"> </div>
            <a href="#dashboard"> Dashboard </a>
            <a href="#findings"> Findings </a>
            <a href="#requires"> Requires </a>
        </div>
        '''

    body = '''
        <div class="container">
        <h1>Report</h1>
        <div class="SGuardHeader">
            <div class='Text'>
                <p>This is an automated report created with the tool <b>Solidity Guard</b>. This tool searches for vulnerabilities in the source code of Solidity Smart contracts with static analysis by traversing its Abstract Syntax Tree (AST). There are several detectors developed, that can find:
                <u>Reentrancy</u> vulnerabilities, unchecked low level calls, <u>selfdestructs</u> not protected, <u>tx.origin</u> usage, possible <u>overflows & underflows</u> vulnerabilities and <u>timestamps</u> calls. 
                Some advices to the developer are given as well, as reminders to review the integrity and correctness of <u>delegatecall</u>, and possible <u>denial of services</u> findings, due to for and while loops.
                Another functionality created is a <u>require checker</u>, that will recommend the use of a modifier when a require is found 3 or more times. 
                The findings will be shown in the next dashboard. </p>   
            </div>
            <div class='logo'>
                <img src="icon.png" alt="Logo" width="100" height="100">
                <div class='Links'>
                    <a href="github.com/ferrabled/SolidiyGuard">Github</a>
                    <a href="mailto:ferrabled@gmail.com">Contact</a>
                </div>
            </div>
        </div>
        </div>
    '''

    footer = '''
        </body>
        </html>
    '''
    rec_Text = '''
        </div>
    '''

    f_header = '''
        <div class="container" id="findings">
            <h2>Findings</h2> 
    '''

    f_footer = '''
        </div>
        '''
    f_warning = ""
    f_vulns = ""
    cont = 0
    
    numwarn = 0
    for finding in findings:
        vuln = finding[0]
        vuln_type = finding[1]
        if(recommendations != None):
            recom = recommendations[cont]
            rec_Text = '''
                <div class="info-row">
                    <h3>Recommendation</h3>
                    <p> Our AI recommender has said the following: </p>
                    <p>''' + recom + '''</p>
                </div>
            </div>
            '''
        location = generate_location(finding, functions[cont])
        # Warnings are attached to the end
        warnings = ['modifier', 'mutex', 'require owner', 'onlyOwner', 'private', 'nonCall', 'micro_outdated', 'block.timestamp', 'block.number', 'for', 'while', 'advisory']
        if(finding[1] in warnings):
            numwarn += 1
            f_warning += '''
                <div class="finding">
                    <div class="title">
                        <h2>''' + json_data[vuln][vuln_type]["vulnerability"] + '''</h2>
                        <div class="warn">Warning</div>
                    </div>
                    <div class="info-row">
                        <h3>Description</h3>
                        <p>''' + json_data[vuln][vuln_type]["description"] + '''</p>
                    </div>
                    <div class="info-row">
                        <h3>Code Location</h3>
                        ''' + location + rec_Text
        else:
            f_vulns +='''
                <div class="finding">
                    <div class="title">
                        <h2>''' + json_data[vuln][vuln_type]["vulnerability"] + '''</h2>
                        <div class="vuln"><b>Vulnerability</b></div>
                    </div>
                    <div class="info-row">
                        <h3>Description</h3>
                        <p>''' + json_data[vuln][vuln_type]["description"] + '''</p>
                    </div>
                    <div class="info-row">
                        <h3>Code Location</h3>
                        ''' + location + rec_Text
        cont += 1

    require_block = generate_require(requires)
    numvulns = data[5] - numwarn
    dashboard = generate_dashboard(data, numvulns, numwarn)

    file_rel_path = "./report.html"
    file_path = os.path.abspath(os.path.join(os.getcwd(), file_rel_path))
    with open(file_path, "w") as file:
        file.write(header)
        file.write(pageheader)
        file.write(body)
        file.write(dashboard)
        file.write(f_header)
        file.write(f_vulns)
        file.write(f_warning)
        file.write(f_footer)
        file.write(require_block)
        file.write(footer)
    print("Report generated")


def generate_dashboard(data, numvulns, numwarn):
    print(data)
    print("DATA")
    dashboard = '''
        <div class="container" id="dashboard">
            <h2>Dashboard</h2>
            <div class="dash-row">
            <div class="analyzed">
                <div class="dcard">
                    <h3>Lines of code</h3>
                    <h2>''' + str(data[0]) + '''</h2>
                </div>
                <div class="dcard">
                    <h3>Contracts</h3>
                    <h2>''' + str(data[1]) + '''</h2>
                </div>
                <div class="dcard">
                    <h3>Functions</h3>
                    <h2>''' + str(data[2]) + '''</h2>
                </div>
            </div>
            <div class="findings">
                <div class="dcard">
                    <h3>Emits</h3>
                    <h2>''' + str(data[3]) + '''</h2>
                </div>
                <div class="dcard">
                    <h3>Requires</h3>
                    <h2>''' + str(data[4][0]) + '''</h2>
                </div>
                <div class="dcard">
                    <h3>Repeated Requires</h3>
                    <h2>''' + str(data[4][1]) + '''</h2>
                </div>
            </div>
            <div class="findings">
                <div class="dcard">
                    <h3>Findings</h3>
                    <h2>''' + str(data[5]) + '''</h2>
                </div>
                <div class="dcard">
                    <h3>Vulns.</h3>
                    <h2>''' + str(numvulns) + '''</h2>
                </div>
                <div class="dcard">
                    <h3>Warnings</h3>
                    <h2>''' + str(numwarn) + '''</h2>
                </div>
            </div>
            </div>
        </div>
    
    '''
    return dashboard

def generate_require(requires):
    print("Generating require report")
    require_header = '''
        <div class="container" id="requires">
            <h2>Requires</h2>
            <div class="info-row">
                <h4>The following requires have been found several times. It is advisabe to replace them with a modifier</h4>
            </div>
        <div class="requires-grid">
    '''
    require_cards = ""
    if(len(requires) > 0):
        for require in requires:
            require_string = require[0].strip()
            if('//' in require_string):
                require_string = (require_string.split("//")[0])
            modifier =  '''modifier << NAME_OF_YOUR_MODIFIER >> () { \n    ''' + require_string + '''\n    _; \n } '''
            #Delete any comment if the require has it, it's not needed
            require_cards += '''
                <div class="require_card">
                    <p> The following require appears ''' + str(len(require[1])) + ''' times in the contract at lines ''' + str(require[1]) + '''
                    </p><pre>''' + str(require_string) + '''</pre>
                    <p> Please consider using the following modifier. It will save gas and make your code more efficient. </p> 
                    <pre class="modifier">''' + modifier + '''</pre>
                </div>''' 
    else:
        require_cards += '''
                <div class="require_card">
                    <p> No require has been found repeated more than 3 times in the contract </p>
                </div>
        '''
    require_footer = '''
            </div>
        </div>
    '''
    require_block = require_header + require_cards + require_footer
    return require_block

def generate_location(finding, fun):
    if(finding[2] != 0):
        text = '''<p> The previous vulnerability has been found in the contract ''' \
        + str(finding[0]) + ''' inside the function ''' \
        + str(finding[0]) + ''' (Line: '''+ str(finding[2]) +''')</p>''' \
        + '''<pre>''' + fun + '''</pre></div>'''
    else:
        text= '''<p> The previous vulnerability has been found in the contract definition </p></div>'''
    return text

def generate_report(findings: list, recommendations: list, functions: list, requires: list, data: list):
    print(data)
    print("DATA")
    if len(findings) == 0:
        print("No vulnerabilities found")
        return
    print("Generating final report... ")
    generate_html(findings, recommendations, functions, requires, data)