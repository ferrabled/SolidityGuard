import json
import sys
import os

# Get the path to the JSON file
base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
# Get the path to the JSON file
json_path = os.path.join(base_path, "utils", "data.json")
data = json.load(open(json_path, "r"))

def generate_html(findings: list, recommendations: list, functions: list, requires: list, dashboard: str):
    print("Generating html report")
    header = '''
        <!DOCTYPE html>
        <html>
        <head>
        <link rel="stylesheet" href="style.css">
        <title>Report</title>
        </head>
    '''
    body = '''
        <body>
        <h1>Report</h1>
        <p>This is an automated report created with the tool</p>
    '''

    footer = '''
        </body>
        </html>
    '''
    rec_Text = '''
        </div>
    </div>'''

    f_warning = ""
    f_vulns = ""
    cont = 0
    
    for finding in findings:
        vuln = finding[0]
        vuln_type = finding[1]
        if(recommendations != None):
            recom = recommendations[cont]
            rec_Text = '''
                <div class="info-row">
                    <h3>Recommendation</h3>
                    <p> Our Chatbot has recommended the following: </p>
                    <p>''' + recom + '''</p>
                </div>
            </div>
            '''
        location = generate_location(finding, functions[cont])
        # TODO check if the finding is a warning instead of a vulnerability, 
        # attach it to the end
        warnings = ['modifier', 'mutex', 'require owner', '', '']
        if(finding[1] in warnings):
            f_warning += '''
                <div class="finding">
                    <h2>''' + data[vuln][vuln_type]["vulnerability"] + '''</h2>
                    <div class="info-row">
                        <h3>Description</h3>
                        <p>''' + data[vuln][vuln_type]["description"] + '''</p>
                    </div>
                    <div class="info-row">
                        <h3>Code Location</h3>
                        ''' + location + rec_Text
        else:
            f_vulns +='''
                <div class="finding">
                    <h2>''' + data[vuln][vuln_type]["vulnerability"] + '''</h2>
                    <div class="info-row">
                        <h3>Description</h3>
                        <p>''' + data[vuln][vuln_type]["description"] + '''</p>
                    </div>
                    <div class="info-row">
                        <h3>Code Location</h3>
                        ''' + location + rec_Text
        cont += 1

    require_block = generate_require(requires)

    file_rel_path = "./report.html"
    file_path = os.path.abspath(os.path.join(os.getcwd(), file_rel_path))
    with open(file_path, "w") as file:
        file.write(header)
        file.write(body)
        file.write(dashboard)
        file.write(f_vulns)
        file.write(f_warning)
        file.write(require_block)
        file.write(footer)
    print("Report generated")


def generate_dashboard(data):
    dashboard = '''
        <div class="dashboard">
            <h2>Dashboard</h2>
            <div class="dash-row">
            <div class="analyzed">
                <div class="dcard">
                    <h3>Lines of code</h3>
                    <p>''' + str(data[0]) + '''</p>
                </div>
                <div class="dcard">
                    <h3>Contracts</h3>
                    <p>''' + str(data[1]) + '''</p>
                </div>
                <div class="dcard">
                    <h3>Functions</h3>
                    <p>''' + str(data[2]) + '''</p>
                </div>
            </div>
            <div class="findings">
                <div class="dcard">
                    <h3>Emits</h3>
                    <p>''' + str(data[3]) + '''</p>
                </div>
                <div class="dcard">
                    <h3>Requires</h3>
                    <p>''' + str(data[4][0]) + '''</p>
                </div>
                <div class="dcard">
                    <h3>Repeated Requires</h3>
                    <p>''' + str(data[4][1]) + '''</p>
                </div>
            </div>
            <div class="findings">
                <div class="dcard">
                    <h3>Findings</h3>
                    <p>''' + str(data[5]) + '''</p>
                </div>
            </div>
            </div>
        </div>
    
    '''
    return dashboard

def generate_require(requires):
    print("Generating require report")
    require_header = '''
        <div class="requires">
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

# TODO location can change if it's a version vulnerability
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
    if len(findings) == 0:
        print("No vulnerabilities found")
        return
    print("Generating final report... ")
    dashboard = generate_dashboard(data)
    generate_html(findings, recommendations, functions, requires, dashboard)