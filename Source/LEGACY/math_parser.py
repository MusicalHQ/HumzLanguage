operators = "*/+-"
expression = "(7+(5+4)+(23*(443+2*(123*123))))"

class math_parser:
    def __init__(self):
        self.possible_variables = ["a","b","c","d","e","f","g","h"]

    def are_brackets(self,queue):
        for i in queue:
            if "(" in queue[i] or ")" in queue[i]:
                return True
        return False

    def evaluate_brackets(self,expression):
        expression = "(" + expression + ")"
        queue,expression = self.replace_with_variables(expression)
        expressions = [expression]
        while self.are_brackets(queue):
            for i in queue:
                new_queue,new_expression = self.replace_with_variables(queue[i])
                queue[i] = new_expression
                queue = {**queue,**new_queue}
        return queue

    def replace_with_variables(self,expression):
        queue,expression_ = self.expand(expression)
        while "(" in expression_:
            queue,expression_ = self.expand(expression)[0]
        for i in queue:
            expression = expression.replace(str("(" + queue[i] + ")"),str(i))
        return queue,expression

    def expand(self,expression):
        queue = {}
        while "(" in expression and ")" in expression:
            new_var = self.possible_variables.pop(-1)
            x,y = self.get_brackets(expression)
            queue[new_var] = expression[x:y][1:-1]
            expression = expression[:x] + expression[y:]
        return queue,expression

    def get_brackets(self,expression):
        for idx,i in enumerate(expression):
            if i == "(":
                break
        x = 1
        y = idx
        while not x == 0:
            y += 1
            if expression[y] == "(":
                x += 1
            if expression[y] == ")":
                x -= 1
        return idx,y+1

m = math_parser()
print(m.evaluate_brackets(expression))
