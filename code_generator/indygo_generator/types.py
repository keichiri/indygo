class FunctionParameter:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def resolve_alias(self, type_map):
        self.type = type_map.get(self.type, self.type)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.type} {self.name}'


class CallbackDeclaration:
    def __init__(self, return_type, parameters):
        self.return_type = return_type
        self.parameters = parameters

    def resolve_alias(self, type_map):
        self.return_type = type_map.get(self.return_type, self.return_type)
        for param in self.parameters:
            param.resolve_alias(type_map)

    @property
    def type(self):
        return f'{self.return_type} (*)({", ".join([param.type for param in self.parameters])})'

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.return_type} (*cb)({", ".join(str(param) for param in self.parameters)})'


class FunctionDeclaration:
    def __init__(self, name, return_type, parameters):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters

    def resolve_alias(self, type_map):
        self.return_type = type_map.get(self.return_type, self.return_type)

        for param in self.parameters:
            param.resolve_alias(type_map)

    @property
    def has_complex_callback_result(self):
        return len(self.parameters[-1].parameters) > 2

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'Name:{self.name}; Return type: {self.return_type}. Params: {", ".join(str(param) for param in self.parameters)}'