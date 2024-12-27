import ASTNodeDefs as AST
class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.current_char = self.code[self.position]
        self.tokens = []
    
    # Move to the next position in the code increment by one.
    def advance(self):
        self.position += 1
        if self.position >= len(self.code):
            self.current_char = None
        else:
            self.current_char = self.code[self.position]

    # If the current char is whitespace, move ahead.
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Tokenize the identifier.
    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return ('IDENTIFIER', result)
    

    # Tokenize numbers, including float handling
    def number(self):
        result = ''
        # TODO: Update this code to handle floating-point numbers 
        is_float = False #set to false originally

        # this will collect all number digits that come before the dot
        while self.current_char is not None and self.current_char.isdigit():
            result = result + self.current_char
            self.advance()

        # first we will check if this is a float to handle dots
        if self.current_char == '.':
            is_float = True
            result = result + self.current_char  # increment result
            self.advance()

            # this will collect all number digits that come after the dot
            post_number_digit = ''
            while self.current_char is not None and self.current_char.isdigit():
                post_number_digit = post_number_digit + self.current_char  # increment result
                self.advance()

            # this will make sure there are digits following the dot for a valid float
            if not post_number_digit:
                raise ValueError(f"Invalid float format at position {self.position}")

            result = result + post_number_digit  # add post-decimal digits to the result

        if is_float:
            return ('FNUMBER', float(result))
        else:
            return ('NUMBER', int(result))
        
    def token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                ident = self.identifier()
                if ident[1] == 'if':
                    return ('IF', 'if')
                elif ident[1] == 'else':
                    return ('ELSE', 'else')
                elif ident[1] == 'while':
                    return ('WHILE', 'while')
                elif ident[1] == 'int':
                    return ('INT', 'int')
                elif ident[1] == 'float':
                    return ('FLOAT', 'float')
                return ident  # Generic identifier
            if self.current_char.isdigit() or self.current_char == '.':
                return self.number()
            if self.current_char == '+':
                self.advance()
                return ('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return ('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return ('MULTIPLY', '*')
            if self.current_char == '/':
                self.advance()
                return ('DIVIDE', '/')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('EQ', '==')
                return ('EQUALS', '=')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('NEQ', '!=')
            if self.current_char == '<':
                self.advance()
                return ('LESS', '<')
            if self.current_char == '>':
                self.advance()
                return ('GREATER', '>')
            if self.current_char == '(':
                self.advance()
                return ('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return ('RPAREN', ')')
            if self.current_char == ',':
                self.advance()
                return ('COMMA', ',')
            if self.current_char == ':':
                self.advance()
                return ('COLON', ':')
            
            # TODO: Implement handling for '{' and '}' tokens here (see `tokens.txt` for exact names)
            if self.current_char == '{': #checking for LBRACE and RBRACE, respectively 
                self.advance()
                return ('LBRACE', '{')
            if self.current_char == '}':
                self.advance()
                return ('RBRACE', '}')
                        
            if self.current_char == '\n':
                self.advance()
                continue

            raise ValueError(f"Illegal character at position {self.position}: {self.current_char}")

        return ('EOF', None)

    # Collect all the tokens in a list.
    def tokenize(self):
        while True:
            token = self.token()
            self.tokens.append(token)
            if token[0] == 'EOF':
                break
        return self.tokens

import ASTNodeDefs as AST

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = tokens.pop(0)
        # Use these to track the variables and their scope
        self.symbol_table = {'global': {}}
        self.scope_counter = 0
        self.scope_stack = ['global']
        self.messages = []

    def error(self, message):
        self.messages.append(message)
    
    def advance(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)

    # TODO: Implement logic to enter a new scope, add it to symbol table, and update `scope_stack`
    def enter_scope(self):
        # this will increment the scope counter to obtain distinct scope names
        self.scope_counter = self.scope_counter + 1
        unique_named_scope = f'scope_{self.scope_counter}'
        # this will set an additional scope in the symbol table
        self.symbol_table[unique_named_scope] = {}
        self.scope_stack.append(unique_named_scope)

    # TODO: Implement logic to exit the current scope, removing it from `scope_stack`
    def exit_scope(self):
        # get rid of the present scope from stack
        current_scope = self.scope_stack.pop()
        # alternatively, delete the scope from the symbol table if it is no longer required

    # Return the current scope name
    def current_scope(self):
        return self.scope_stack[-1]

    # TODO: Check if a variable is already declared in the current scope; if so, log an error
    def checkVarDeclared(self, identifier):
        # this wil obtain the present scope
        current_scope = self.current_scope()
        # check variable declaration
        check_declaration = identifier in self.symbol_table[current_scope]
        if check_declaration:
            # error if the variable is already declared and defined
            self.error(f"Variable {identifier} has already been declared in the current scope")
        return check_declaration

    # TODO: Check if a variable is declared in any accessible scope; if not, log an error
    def checkVarUse(self, identifier):
        # obtain the type for the variable from the symbol table
        var_type = self.get_variable_type(identifier)
        if var_type is None:
            # error if not defined in some accessible/ready scope
            self.error(f"Variable {identifier} has not been declared in the current or any enclosing scopes")
            return False
        # true if declared/defined
        return True

    # TODO: Check type mismatch between two entities; log an error if they do not match
    def checkTypeMatch2(self, vType, eType, var, exp):
        if vType is None or eType is None:
            # if statement to return false if types are not known
            return False
        if vType != eType:
            self.error(f"Type Mismatch between {vType} and {eType}")
            return False #if there is a type mismatch, this if statement will then return false, if a match is found then return true
        return True

    # TODO: Implement logic to add a variable to the current scope in `symbol_table`
    def add_variable(self, name, var_type):
        current_scope = self.current_scope() #find the current scope
        self.symbol_table[current_scope][name] = var_type #increment symbol table with the respective variable for the current scope
        count_scope = len(self.symbol_table[current_scope]) #track variable count within scope (used to debug if there's an error)

    # TODO: Retrieve the variable type from `symbol_table` if it exists
    def get_variable_type(self, name):
    # this will iterate through the scope stack from inside to outside
        variable_type = next(
            (self.symbol_table[scope][name] for scope in reversed(self.scope_stack) if name in self.symbol_table[scope]),
            None # None if not found
        )

        return variable_type  # if variable definition is found, return it's type or None if not found

    def parse(self):
        return self.program()

    def program(self):
        statements = []
        while self.current_token[0] != 'EOF':
            statements.append(self.statement())
        return AST.Block(statements)

    # TODO: Modify the `statement` function to dispatch to declare statement
    def statement(self):
        # variable declaration/definition statements
        if self.current_token[0] in ['INT', 'FLOAT']:
            return self.decl_stmt()
        
        # originally check these control flow statements
        elif self.current_token[0] == 'IF':
            return self.if_stmt()
        elif self.current_token[0] == 'WHILE':
            return self.while_stmt()

        # this will handle statements that are identifier-based
        elif self.current_token[0] == 'IDENTIFIER':
            if self.peek() == 'EQUALS':  
                return self.assign_stmt()
            elif self.peek() == 'LPAREN':  # include a function call
                return self.function_call()
            else:
                # raising an error for an incorrect token following an identifier
                raise ValueError(f"Unexpected token after identifier: {self.current_token}")

        # if any other unexpected tokens are encountered, raise an error
        else:
            raise ValueError(f"Unexpected token: {self.current_token}")

    # TODO: Implement the declaration statement and handle adding the variable to the symbol table
    def decl_stmt(self):
        """
        Parses a declaration statement.
        Example:
        int x = 5
        float y = 3.5
        TODO: Implement logic to parse type, identifier, and initialization expression and also handle type checking
        """
        # check var type either int or float
        var_type = self.current_token[1]  # this will extract the respective type
        self.advance()  # advance to next token

        # varify the next token is an identifier 
        if self.current_token[0] == 'IDENTIFIER':  # check validity
            var_name = self.current_token[1]  # extract similar to above, if an issue is found, raise an error
        else:
            raise ValueError(f"Expected IDENTIFIER after type, got {self.current_token[0]}")

        # checking pre variable declarations
        if not self.checkVarDeclared(var_name):  # continue if there is no redeclaration
            self.add_variable(var_name, var_type)  # append to symbol table
        self.advance()  # advance like before

        # checking if = symbol follows selected identifier
        if self.current_token[0] == 'EQUALS':  # verify = validity
            self.advance()  # as before, advance
        else:
            raise ValueError(f"Expected '=', got {self.current_token[0]}")

        # evaluate the starting statement
        expression = self.expression()  

        # checking type compatability
        exp_type = expression.value_type  
        if exp_type is not None:  
            self.checkTypeMatch2(var_type, exp_type, var_name, expression)

        # finally give the AST node for the definition.
        return AST.Declaration(var_type, var_name, expression)

    # TODO: Parse assignment statements, handle type checking
    def assign_stmt(self):
        """
        Parses an assignment statement.
        Example:
        x = 10
        x = y + 5
        TODO: Implement logic to handle assignment, including type checking.
        """
        # as the prior process, this time parse identifier and extract var name
        var_name = self.current_token[1]  

        # check variable declaration, if declared then obtain its type and if not declared, set to None
        if self.checkVarUse(var_name):  
            var_type = self.get_variable_type(var_name)
        else:  
            var_type = None
        self.advance()  

        # check for =
        if self.current_token[0] == 'EQUALS':  
            self.advance()  
        else:
            raise ValueError(f"Expected '=', got {self.current_token[0]}")

        expression = self.expression()  

        # checking for compatability checks
        if var_type is not None and expression.value_type is not None:  
            self.checkTypeMatch2(var_type, expression.value_type, var_name, expression)

        # finally return the AST node 
        return AST.Assignment(var_name, expression)

    # TODO: Implement the logic to parse the if condition and blocks of code
    def if_stmt(self):
        """
        Parses an if-statement, with an optional else block.
        Example:
        if condition {
            # statements
        }
        else {
            # statements
        }
        TODO: Implement the logic to parse the if condition and blocks of code.
        """
        # advance pass if
        self.advance()  

        # iterate boolean expression
        condition = self.boolean_expression()  

        # check that { indicates the start of the then block and corresponding statements
        if self.current_token[0] == 'LBRACE':  
            self.advance()  
        else:
            raise ValueError(f"Expected '{{', got {self.current_token[0]}")

        # enter the new scope
        self.enter_scope()
        # iterate through then block conditions
        then_block = self.block()
        self.exit_scope()

        # this will check for else block (optional block)
        else_block = None
        if self.current_token[0] == 'ELSE': 
            self.advance() 
            # similar to above, statement to check { marks beginning
            if self.current_token[0] == 'LBRACE':  
                self.advance()  
            else:
                raise ValueError(f"Expected '{{' after 'else', got {self.current_token[0]}")

            # similar process as above here
            self.enter_scope()
            else_block = self.block()
            self.exit_scope()

        # lastly return AST statement 
        return AST.IfStatement(condition, then_block, else_block)

    # TODO: Implement the logic to parse while loops with a condition and a block of statements
    def while_stmt(self):
        """
        Parses a while-statement.
        Example:
        while condition {
            # statements
        }
        TODO: Implement the logic to parse while loops with a condition and a block of statements.
        """
        # advance pass while, similar procedure as above
        self.advance() 

        # iterate and parse over boolean expression
        condition = self.boolean_expression()  

        # check { indicates start of block
        if self.current_token[0] == 'LBRACE':  
            self.advance()  
        else:
            raise ValueError(f"Expected '{{', got {self.current_token[0]}")

        self.enter_scope()
        # set an id to track scope counter if there is an error (easier to debug)
        check_loop = f"loop_{self.scope_counter}" 
        # parse block expressions
        block = self.block()
        self.exit_scope()

        # return final AST
        return AST.WhileStatement(condition, block)

    # TODO: Implement logic to capture multiple statements as part of a block
    def block(self):
        """
        Parses a block of statements. A block is a collection of statements grouped by `{}`.
        Example:
        
        x = 5
        y = 10
        
        TODO: Implement logic to capture multiple statements as part of a block.
        """
        # define a list to hold block statements and expressions
        statements = []
        # parse till } is found
        while self.current_token[0] != 'RBRACE':
            statements.append(self.statement())  # iterate and parse, append to statements
        self.advance()
        return AST.Block(statements)

    # TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence and type checking
    def expression(self):
        """
        Parses an expression. Handles operators like +, -, etc.
        Example:
        x + y - 5
        TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence and type checking.
        """
        # parse through left side operand
        left = self.term()

        # iterate through binary operators
        while self.current_token[0] in ['PLUS', 'MINUS']:
            # find current op
            op = self.current_token[0]
            self.advance() 
            # traverse right side operand
            right = self.term()
            # check operand type, then compatability
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            # It is expected that the resulting type matches the type of the left operand.
            left = AST.BinaryOperation(left, op, right, value_type = left.value_type)

        return left

    # TODO: Implement parsing for boolean expressions and check for type compatibility
    def boolean_expression(self):
        """
        Parses a boolean expression. These are comparisons like ==, !=, <, >.
        Example:
        x == 5
        TODO: Implement parsing for boolean expressions and check for type compatibility.
        """
        # as above, traverse left side operand
        left = self.expression()

        # this will check for any comparasion operator and if it's found, obtain it
        if self.current_token[0] in ['EQ', 'NEQ', 'LESS', 'GREATER']:
            op = self.current_token[0]
            self.advance()
            # now traverse right side operand
            right = self.expression()
            # check for compatability only if the types are none for left.value_type and right.value_type
            if left.value_type is not None and right.value_type is not None:
                self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            return AST.BooleanExpression(left, op, right)

        else:
            # error raised if proper comparasion operator not found
            raise ValueError(f"Expected comparison operator, got {self.current_token[0]}")
        

    # TODO: Implement parsing for multiplication and division and check for type compatibility
    def term(self):
        """
        Parses a term. A term consists of factors combined by * or /.
        Example:
        x * y / z
        TODO: Implement parsing for multiplication and division and check for type compatibility.
        """
        # as above, traverse left side operand
        left = self.factor()
        # valid operators set as multiply and divide
        operators = ['MULTIPLY', 'DIVIDE']
        # iterate through * or / via for loop and obtain operator if conditions met
        for _ in iter(lambda: self.current_token[0] in operators, False):
            op = self.current_token[0]
            self.advance()  
            right = self.factor()
            # checking for compatability if types are not None and known
            if left.value_type is not None and right.value_type is not None:
                self.checkTypeMatch2(left.value_type, right.value_type, left, right)
                result_type = left.value_type  # assuming that types indeed match
            else:
                result_type = None  
            left = AST.BinaryOperation(left, op, right, value_type=result_type)

        return left
        
    def factor(self):
        if self.current_token[0] == 'NUMBER':
            # handle int
            num = self.current_token[1]
            self.advance()
            return AST.Factor(num, 'int')
        elif self.current_token[0] == 'FNUMBER':
            # handle float
            num = self.current_token[1]
            self.advance()
            return AST.Factor(num, 'float')
        
        
        elif self.current_token[0] == 'IDENTIFIER':
            # TODO: Ensure that you parse the identifier correctly, retrieve its type from the symbol table, and check if it has been declared in the current or any enclosing scopes.
            # this will evaluate the identifier, get its type from the symbol database, and see if it was declared
            var_name = self.current_token[1]
            if not self.checkVarUse(var_name):  # check variable declaration, if None, set to None for undefined/undeclared variables
                var_type = None  
            else:
                var_type = self.get_variable_type(var_name)  # this will acquire the variable type from the symbol table
            self.advance()  # advance past identifier
            
            return AST.Factor(var_name, var_type)
        

        elif self.current_token[0] == 'LPAREN':
            self.advance()
            expr = self.expression()
            self.expect('RPAREN')
            return expr
        else:
            raise ValueError(f"Unexpected token in factor: {self.current_token}")

    def function_call(self):
        func_name = self.current_token[1]
        self.advance()
        self.expect('LPAREN')
        args = self.arg_list()
        self.expect('RPAREN')

        return AST.FunctionCall(func_name, args)

    def arg_list(self):
        """
        Parses a list of function arguments.
        Example:
        (x, y + 5)
        """
        args = []
        if self.current_token[0] != 'RPAREN':
            args.append(self.expression())
            while self.current_token[0] == 'COMMA':
                self.advance()
                args.append(self.expression())

        return args

    def expect(self, token_type):
        if self.current_token[0] == token_type:
            self.advance()
        else:
            raise ValueError(f"Expected token {token_type}, but got {self.current_token[0]}")

    def peek(self):
        return self.tokens[0][0] if self.tokens else None


# test cases that were implemented to briefly test, this is more brief test cases written like pseudocode
#for scope redeclaration (what this could look like):
"""
    int a = 10
    {
        int a = 20
        a = a + 1
    }
    a = a + 2
"""


#for type mismatch (what this could look like):
"""
    int x = 10
    float y = 5.5
    int z = x + y
"""

#undeclared/undefined variables within nested scope (what this could look like): 
"""
    {
        int a = 30
        {
            b = a + 10
        }
    }
"""