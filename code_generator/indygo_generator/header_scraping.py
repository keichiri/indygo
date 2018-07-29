import re


from indygo_generator.function import FunctionDeclaration, FunctionParameter, CallbackDeclaration


_REPLACEMENT_TABLE = str.maketrans({'\n': ' ', '\t': ' '})
_MULTI_SPACE_PATT = re.compile('\s{2,}')
_HEADER_FUNCTION_PATT = re.compile('extern\s+?(?P<declaration>[\w\s]+?indy.+?;)', re.DOTALL)
_HEADER_TYPEDEF_PATT = re.compile('typedef\s+?(?P<types>[\w\s]+?);')
_FUNCTION_DECLARATION_PATT = re.compile('(?P<rtype>\w+?)\s+?\(?(?P<fname>[\w*]+?)\)?\((?P<param_string>.+?)\);', re.DOTALL)


class ParsingError(Exception):
    pass


def scrape_header_file(header_file_content):
    declarations = []

    for scrape_result in _HEADER_FUNCTION_PATT.finditer(header_file_content):
        declaration = parse_indy_function_declaration(scrape_result.groupdict()['declaration'])
        declarations.append(declaration)

    type_map = {}

    for scrape_result in _HEADER_TYPEDEF_PATT.finditer(header_file_content):
        alias, c_type = parse_indy_typedef(scrape_result.groupdict()['types'])
        type_map[alias] = c_type

    return declarations, type_map


def parse_indy_typedef(types_string):
    types_string = re.sub(_MULTI_SPACE_PATT, ' ', types_string)
    items = [item for item in types_string.split(' ') if item]

    indy_alias = items[-1]
    c_type = ' '.join(items[:-1])

    return indy_alias, c_type


def parse_indy_function_declaration(declaration):
    function_name, return_type, parameters = _parse_function_declaration(declaration)
    return FunctionDeclaration(function_name, return_type, parameters)


def _parse_function_declaration(declaration):
    declaration = declaration.strip()
    declaration = declaration.translate(_REPLACEMENT_TABLE)
    declaration = re.sub(_MULTI_SPACE_PATT, ' ', declaration)
    scrape_result = _FUNCTION_DECLARATION_PATT.match(declaration)
    if not scrape_result:
        raise ParsingError(f'Failed to match function declaration {declaration}')

    result_items = scrape_result.groupdict()
    return_type = result_items['rtype']
    function_name = result_items['fname'].replace('indy_', '', 1)
    param_string = result_items['param_string'].strip(' ')

    parameters = _parse_function_parameters(param_string)

    return function_name, return_type, parameters


def _parse_function_parameters(parameters_string):
    parameter_strings = _split_parameter_string(parameters_string)
    parameters = []

    for param_string in parameter_strings:
        parameters.append(_parse_parameter(param_string))

    return parameters


# NOTE - assumes one level of nesting
def _split_parameter_string(parameters_string):
    parameter_strings = []
    nested = False
    param_start = 0

    for i in range(len(parameters_string)):
        current_char = parameters_string[i]

        if current_char == ',':
            if i == param_start:
                raise ParsingError(f'Invalid parameters string: {parameters_string}')

            if nested:
                continue

            current_param_string = parameters_string[param_start:i].strip()
            if not current_param_string:
                raise ParsingError(f'Invalid parameters string: {parameters_string}')

            parameter_strings.append(current_param_string)
            param_start = i+1

        elif current_char == '(':
            nested = True
        elif current_char == ')':
            nested = False

    last_param_string = parameters_string[param_start:].strip()
    if not last_param_string:
        raise ParsingError(f'Invalid parameters string: {parameters_string}')

    parameter_strings.append(last_param_string)

    return parameter_strings


def _parse_parameter(parameter_string):
    if _is_function_parameter(parameter_string):
        return _parse_callback_parameter(parameter_string)

    parts = parameter_string.split(' ')
    if len(parts) < 2:
        raise ParsingError(f'Invalid function parameter string: {parameter_string}')

    param_name = parts[-1]
    param_type = ' '.join(parts[:-1])
    return FunctionParameter(param_name, param_type)


def _is_function_parameter(parameter_string):
    return '(' in parameter_string


def _parse_callback_parameter(parameter_string):
    _, return_type, parameters = _parse_function_declaration(parameter_string + ';')
    return CallbackDeclaration(return_type, parameters)

