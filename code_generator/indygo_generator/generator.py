import os

from indygo_generator.header_scraping import scrape_header_file, ParsingError
from indygo_generator.types import FunctionParameter, cgo_to_go_conversion


class GeneratorError(Exception):
    pass


def _callback_name_camel_case(function_name):
    words = function_name.split('_')
    camelcased_words = [words[0]]
    camelcased_words.extend([word.title() for word in words[1:]])
    return ''.join(camelcased_words) + 'Callback'



class Generator:
    @staticmethod
    def _generate_c_proxy_signature(func_declaration):
        passed_params = func_declaration.parameters[:-1]
        c_proxy_declared_params = [FunctionParameter(name='f', type='void *')] + passed_params
        param_string = ', '.join([f'{p.type} {p.name}' for p in c_proxy_declared_params])
        return f'{func_declaration.return_type} indy_{func_declaration.name}_proxy({param_string})'

    @staticmethod
    def _generate_c_proxy_declaration_code(func_declaration):
        return Generator._generate_c_proxy_signature(func_declaration) + ';'

    @staticmethod
    def _generate_c_proxy_code(func_declaration):
        signature_string = Generator._generate_c_proxy_signature(func_declaration)
        param_types_string = ', '.join([p.type for p in func_declaration.parameters])
        cast_string = f'{func_declaration.return_type} (*func)({param_types_string}) = f;'
        callback_name = _callback_name_camel_case(func_declaration.name)
        param_names_string = ', '.join([p.name for p in func_declaration.parameters[:-1]])
        invocation_and_return_string = f'return func({param_names_string}, &{callback_name});'
        c_proxy_code = f'{signature_string}\n{{\n\t{cast_string}\n\t{invocation_and_return_string}\n}}'
        return c_proxy_code

    @staticmethod
    def _generate_callback_result_struct_code(go_function):
        result_struct = go_function.result_struct

        field_declarations = []
        for field in result_struct.fields:
            field_declarations.append(f'{field.name} {field.type}')
        line_sep = "\n\t"
        code = f'type {result_struct.name} struct {{\n\t{line_sep.join(field_declarations)}\n}}'
        return code

    @staticmethod
    def _generate_callback_code(go_function):
        callback = go_function.callback
        export_string = f'//export {callback.name}'
        param_string = ', '.join([f'{param.name} {param.type}' for param in callback.parameters])
        signature_string = f'func {callback.name}({param_string})'
        first_param_name = callback.parameters[0].name
        deregister_call_string = _DEREGISTER_CALL_TEMPLATE.format(first_param_name)

        result_struct = go_function.result_struct
        field_strings = []
        for i, field in enumerate(result_struct.fields):
            # skipping command handle
            arg = callback.parameters[i+1]
            cgo_to_go_conversion_function = cgo_to_go_conversion(arg.type)
            if cgo_to_go_conversion_function:
                field_string = f'{field.name}: {cgo_to_go_conversion_function}({arg.name})'
            else:
                field_string = f'{field.name}: {arg.name}'

            field_strings.append(field_string)

        join_string = ",\n\t\t"
        res_init_string = f'res := &{result_struct.name}{{\n\t\t{join_string.join(field_strings)},\n\t}}'
        res_send_string = 'resCh <- res'

        full_code = f'{export_string}\n{signature_string} {{\n\t{deregister_call_string}{_DEREGISTER_CALL_ERR_CHECK}\n\t{res_init_string}\n\t{res_send_string}\n}}'
        print(full_code)

        return full_code


    def __init__(self, header_dir_path, output_path):
        self._header_dir_path = header_dir_path
        self._output_path = output_path
        self._c_function_declarations = {}

    def _read_header_files(self):
        header_file_contents = {}

        try:
            for header_file_name in os.listdir(self._header_dir_path):
                header_file_path = os.path.join(self._header_dir_path, header_file_name)
                with open(header_file_path, 'r') as f:
                    file_content = f.read()
                    header_file_contents[header_file_name] = file_content
        except OSError as e:
            raise GeneratorError(f'Error while reading header files at path: {self._header_dir_path}') from e

        return header_file_contents

    def _prepare_c_function_declarations(self):
        header_file_contents = self._read_header_files()
        # Small hack to allow parsing regex to be simpler (no need to match enum)
        full_type_map = {'indy_error_t': 'int32_t'}
        c_function_declarations = {}

        try:
            for file_name, file_content in header_file_contents.items():
                declarations, type_map = scrape_header_file(file_content)
                full_type_map.update(type_map)
                c_function_declarations[file_name] = declarations
        except ParsingError as e:
            raise GeneratorError(f'Failed to parse header files at path: {self._header_dir_path}') from e

        for function_declarations in c_function_declarations.values():
            for declaration in function_declarations:
                declaration.resolve_alias(full_type_map)

        self._c_function_declarations = c_function_declarations



_DEREGISTER_CALL_TEMPLATE = 'resCh, err := resolver.DeregisterCall({})'
_DEREGISTER_CALL_ERR_CHECK = """
    if err != nil {
        log.Printf("ERROR: invalid handle in callback.\\n")
        return
    }
"""