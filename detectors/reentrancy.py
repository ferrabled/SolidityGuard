from .language.SolidityVisitor import SolidityVisitor
from .language.SolidityParser import SolidityParser
from detectors.AST_utils import get_function_start_end, TerminalNode

findings = []
lock_variables = []

class SolidityCallVisitor(SolidityVisitor):
    
    def visitStateVariableDeclaration(self, ctx:SolidityParser.StateVariableDeclarationContext):
        # Check if the variable type is 'bool'
        if "bool" in ctx.typeName().getText():
            # Get the variable name
            ## print("Found a bool variable: " + str(ctx.identifier().getText()))
            variable_name = ctx.identifier().getText()
            lock_variables.append(variable_name)
        return super().visitStateVariableDeclaration(ctx)


    def visitFunctionDefinition(self, ctx):
        # Check if the function contains a 'Call' node
        call_node = self.find_call_node(ctx)
        if call_node is not None:
            # Check whether the function has a nonReentrant modifier
            # This modifier from OpenZeppelin is used to prevent reentrancy attacks
            has_nonReentrant = ('nonReentrant') in ctx.modifierList().getText()
            
            call_line = call_node.getPayload().line    
            funcName = ctx.getChild(0).getText()

            if not has_nonReentrant:
                # Obtain the line where the call is
                ## print("LINE: " + str(call_line))
                require_mutex_line, mutex_var = self.find_lock_variables(ctx)
                ## print("Lock variables: " + str(lock_variables))

                if require_mutex_line is not None:
                    # Check if the mutex is being updated prior to the call
                    if require_mutex_line < call_line:
                        print("Mutex is being required prior to the call")
                        # Continue checking if the mutex is being updated before and after the call
                        update_lines = self.check_mutex_update(ctx, mutex_var)
                        if update_lines is not None and update_lines[0] < call_line and update_lines[1] > call_line:
                            print("Possible mutex found in line " + str(require_mutex_line) + "; Function -> " + funcName[8:])
                            start, end = get_function_start_end(call_node)
                            findings.append(['reentrancy', 'mutex', call_line, [start, end]])
                            return super().visitFunctionDefinition(ctx)
                        else:
                            start, end = get_function_start_end(call_node)
                            findings.append(['reentrancy', 'vulnerable', call_line, [start, end]])
                            return super().visitFunctionDefinition(ctx)
                    else:
                        start, end = get_function_start_end(call_node)
                        findings.append(['reentrancy', 'vulnerable', call_line, [start, end]])
                        return super().visitFunctionDefinition(ctx)
                else:
                    print("Possible reentrancy vulnerability found in line " + str(call_line) + "; Function -> " + funcName[8:])
                    start, end = get_function_start_end(call_node)
                    findings.append(['reentrancy', 'vulnerable', call_line, [start, end]])
            else:
                # As it has a nonReentrant modifier, it is not vulnerable to reentrancy     
                print("Possible nonReentrant modifier found in function: " + funcName[8:])   
                start, end = get_function_start_end(call_node)
                findings.append(['reentrancy', 'modifier', call_line, [start, end]])
        return super().visitFunctionDefinition(ctx)


    def check_mutex_update(self, ctx:SolidityParser.FunctionDefinitionContext, mutex_var):
        ctx_list = []
        updateLine = []
        # iterate the nodes and find the mutex in the function, save the ctx in ctx_list
        # As we're in the function definition node, we require the last children, block
        for child in ctx.getChild(-1).children:
            if str(mutex_var) in child.getText() and not 'require' in child.getText():
                # Check if it's being set to true or false
                ctx_list.append(child)

        for ctx in ctx_list:
            # Looking at the Parse Tree, we've just entered block
            # block -> statement -> SimpleStatement -> expressionStatement -> expression | ;
            # We choose the second child to get the line 
            updateLine.append(ctx.getChild(0).getChild(0).getChild(1).getPayload().line)
        
        # find the boolean value of the mutex
        first_boolean = (ctx_list[0].getText().split('=')[1].replace(';', '')) 
        second_boolean = (ctx_list[1].getText().split('=')[1].replace(';', ''))
        ## print("First boolean: " + str(first_boolean) + " Second boolean: " + str(second_boolean) + " Different: " + str((first_boolean != second_boolean)))
        # if the boolean is true, we're looking for a false update and viceversa
        if (first_boolean != second_boolean):
            return updateLine
        else:
            return None
    

    def find_lock_variables(self, ctx:SolidityParser.FunctionDefinitionContext):

        def find_expression_statement_parent(ctx):
            # Iterate the parent nodes until we find the expressionStatement parent
            # This is the parent node of the require statement, it will be checking the mutex
            parent = ctx.parentCtx
            while parent is not None:
                if parent.getRuleIndex() ==  SolidityParser.RULE_expressionStatement and 'require' in parent.getText():
                    print("Require found along with the mutex : " + str(parent.getText()))
                    ## print("On line: " + str(ctx.getPayload().line))
                    return parent
                parent = parent.parentCtx
            return None
        
        # Once we know the boolean variables on the contract [lock_variables]
        # We are going to check if our function (The one which is using 'call') is using one of them
        # If it is, we are going to check if it could be a mutex
        # - First, if it's being checked in a require statement
        # - Second, if the require statement is previous to the call
        # - Third, check if the mutex is being updated prior to the call
        # - Fourth, check if the mutex is being updated after the call
        # If all of this is true, we are going to consider it as a mutex
        # and we are not going to report it as a vulnerability, but as a warning
        
        if isinstance(ctx, TerminalNode):
            if (ctx.getText() in lock_variables):
                print("Possible mutex found: " + ctx.getText())
                
                expr_stmt_parent = find_expression_statement_parent(ctx)
                if expr_stmt_parent is None:
                    print("ExpressionStatement parent not found")
                    return None
                line = ctx.getPayload().line
                ## print("Line: " + str(line))
                return line, ctx.getText()
            return None
        for child in ctx.children:
            call_node = self.find_lock_variables(child)
            if call_node is not None:
                return call_node
        return None, None


    def find_call_node(self, ctx:SolidityParser.FunctionDefinitionContext):
        # Auxiliar function to find the 'call' node in the current context
        if isinstance(ctx, TerminalNode):
            if ctx.getText() == 'call':
                return ctx
            return None
        try:
            for child in ctx.children:
                call_node = self.find_call_node(child)
                if call_node is not None:
                    return call_node
        except Exception as e:
            return None
        return None


