class FunctionParameter:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def resolve_alias(self, type_map):
        self.type = type_map.get(self.type, self.type)


class CallbackDeclaration:
    def __init__(self, rtype, parameters):
        self.return_type = rtype
        self.parameters = parameters

    def resolve_alias(self, type_map):
        self.return_type = type_map.get(self.return_type, self.return_type)
        for param in self.parameters:
            param.resolve_alias(type_map)


class FunctionDeclaration:
    def __init__(self, name, return_type, parameters):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters

    def resolve_alias(self, type_map):
        self.return_type = type_map.get(self.return_type, self.return_type)

        for param in self.parameters:
            param.resolve_alias(type_map)