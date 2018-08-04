from indygo_generator.utils import to_camel_case


_C_TO_GO_TYPE_MAP = {
    'int32_t': 'int32',
    'uint32_t': 'uint32',
    'int16_t': 'int16',
    'uint16_t': 'uint16',
    'char *': 'string',
}


_C_TO_CGO_TYPE_MAP = {
    'char *': '*C.char',
}


_CGO_TO_GO_CONVERSIONS = {
    '*C.char': 'C.GoString',
}


_GO_TO_CGO_TYPE_MAP = {
    'string': '*C.char',
    'int32': 'C.int32_t',
}


_GO_TO_CGO_CONVERSIONS = {
    'string': 'C.CString',
    'int32': 'C.int32_t',
}


_DEFAULT_GO_VALUES = {
    'string': '\"\"',
    'int32': 0,
}


def get_go_type(c_type):
    c_type = c_type.replace('const', '').strip()
    return _C_TO_GO_TYPE_MAP[c_type]


def get_cgo_type(c_type):
    c_type = c_type.replace('const', '').strip()
    cgo_type = _C_TO_CGO_TYPE_MAP.get(c_type)
    return cgo_type or _C_TO_GO_TYPE_MAP[c_type]


def get_cgo_type_for_go_type(go_type):
    return _GO_TO_CGO_TYPE_MAP[go_type]


def cgo_to_go_conversion(cgo_type):
    return _CGO_TO_GO_CONVERSIONS.get(cgo_type)


def go_to_cgo_conversion(go_type):
    return _GO_TO_CGO_CONVERSIONS.get(go_type)


def get_default_go_value(go_type):
    return _DEFAULT_GO_VALUES[go_type]


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

    @property
    def callback_result_additional_types(self):
        return self.parameters[-1].parameters[2:]

    @property
    def callback(self):
        return self.parameters[-1]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'Name:{self.name}; Return type: {self.return_type}. Params: {", ".join(str(param) for param in self.parameters)}'


class GoVariable:
    # NOTE - using "variable" as both a function parameter and a struct field, for simplicity
    def __init__(self, name, type):
        self.name = name
        self.type = type


class GoFunction:
    @classmethod
    def create_from_indy_declaration(cls, function_declaration):
        name = to_camel_case(function_declaration.name)
        name = name[0].title() + name[1:]

        params = []
        # skipping handle and callback - not visible in public API
        for c_param in function_declaration.parameters[1:-1]:
            go_param_name = to_camel_case(c_param.name)
            go_param_type = get_go_type(c_param.type)
            go_param = GoVariable(name=go_param_name, type=go_param_type)
            params.append(go_param)

        return_types = []
        for returned_c_field in function_declaration.callback.parameters[2:]:
            returned_go_type = get_go_type(returned_c_field.type)
            return_types.append(returned_go_type)
        return_types.append('error')

        callback_name = name[0].lower() + name[1:] + 'Callback'
        callback_parameters = []
        for param in function_declaration.callback.parameters:
            go_param_name = to_camel_case(param.name)
            cgo_param_type = get_cgo_type(param.type)
            cgo_param = GoVariable(go_param_name, cgo_param_type)
            callback_parameters.append(cgo_param)
        callback = GoCallback(callback_name, callback_parameters)

        result_struct_name = name[0].lower() + name[1:] + 'Result'
        result_struct_fields = []
        for returned_c_field in function_declaration.callback.parameters[1:]:
            go_type = get_go_type(returned_c_field.type)
            go_name = to_camel_case(returned_c_field.name)
            go_field = GoVariable(name=go_name, type=go_type)
            result_struct_fields.append(go_field)

        result_struct = GoStruct(result_struct_name, result_struct_fields)

        return cls(name, params, return_types, callback, result_struct, function_declaration)


    def __init__(self, name, parameters, return_types, callback, result_struct, indy_function):
        self.name = name
        self.parameters = parameters
        self.return_types = return_types
        self.callback = callback
        self.result_struct = result_struct
        self.indy_function = indy_function


class GoCallback:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters


class GoStruct:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields