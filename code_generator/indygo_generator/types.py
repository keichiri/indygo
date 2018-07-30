from indygo_generator.utils import to_camel_case


_C_TO_GO_TYPE_MAP = {
    'int32_t': 'int32',
    'uint32_t': 'uint32',
    'int16_t': 'int16',
    'uint16_t': 'uint16',
    'char *': 'string',
}


def get_go_type(c_type):
    c_type = c_type.replace('const', '').strip()
    return _C_TO_GO_TYPE_MAP[c_type]


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

    def go_function(self):
        name = to_camel_case(self.name)
        name = name[0].title() + name[1:]

        # skipping command handle and callback
        c_params = self.parameters[1:-1]
        go_params = []
        for c_param in c_params:
            go_param_type = get_go_type(c_param.type)
            go_param_name = to_camel_case(c_param.name)
            go_param = GoFunctionParameter(go_param_name, go_param_type)
            go_params.append(go_param)

        return_types = ['error']
        additional_returned_types = self.callback_result_additional_types
        for returned_type in additional_returned_types:
            go_type = get_go_type(returned_type)
            return_types.append(go_type)

        return GoFunction(name, go_params, return_types)

    @property
    def has_complex_callback_result(self):
        return len(self.parameters[-1].parameters) > 2

    @property
    def callback_result_additional_types(self):
        return self.parameters[-1].parameters[2:]


    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'Name:{self.name}; Return type: {self.return_type}. Params: {", ".join(str(param) for param in self.parameters)}'


class GoFunctionParameter:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class GoFunction:
    def __init__(self, name, parameters, return_types):
        self.name = name
        self.parameters = parameters
        self.return_types = return_types
