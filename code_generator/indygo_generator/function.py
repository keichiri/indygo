class FunctionParameter:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class CallbackDeclaration:
    def __init__(self, rtype, parameters):
        self.rtype = rtype
        self.parameters = parameters


class FunctionDeclaration:
    def __init__(self, name, return_type, parameters):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters
