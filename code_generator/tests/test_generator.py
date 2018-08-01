import unittest
import re
from unittest.mock import patch, Mock

from indygo_generator.generator import Generator
from indygo_generator.types import CallbackDeclaration, FunctionDeclaration, FunctionParameter, GoFunction

from . import TEST_HEADER_FILE


_WHITESPACE_PATT = re.compile('\s{2,}|\n|\t')


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        params = [
            FunctionParameter(name='command_handle', type='int32_t'),
            FunctionParameter(name='wallet_handle', type='int32_t'),
            FunctionParameter(name='submitter_did', type='const char *'),
            FunctionParameter(name='request_json', type='const char *'),
            CallbackDeclaration(
                return_type='void',
                parameters=[
                    FunctionParameter(name='xcommand_handle', type='int32_t'),
                    FunctionParameter(name='err', type='int32_t'),
                    FunctionParameter(name='signed_request_json', type='const char *'),
                ])
        ]
        self.indy_function = FunctionDeclaration(name='sign_request',
                                                 return_type='int32_t',
                                                 parameters=params)

        self.go_function = GoFunction.create_from_indy_declaration(self.indy_function)

    @patch.object(Generator, '_read_header_files')
    def test_prepare_c_function_declarations(self, read_header_files_patch):
        read_header_files_patch.return_value = {'indy_file_1': TEST_HEADER_FILE}
        generator = Generator(Mock(), Mock())

        generator._prepare_c_function_declarations()

        self.assertEqual(len(generator._c_function_declarations), 1)
        declarations = generator._c_function_declarations['indy_file_1']
        self.assertEqual(len(declarations), 3)

        declaration_1 = declarations[0]
        self.assertEqual(declaration_1.name, 'sign_and_submit_request')
        self.assertEqual(declaration_1.return_type, 'int32_t')
        self.assertEqual(len(declaration_1.parameters), 6)
        self.assertEqual(declaration_1.parameters[0].name, 'command_handle')
        self.assertEqual(declaration_1.parameters[0].type, 'int32_t')
        self.assertEqual(declaration_1.parameters[1].name, 'pool_handle')
        self.assertEqual(declaration_1.parameters[1].type, 'int32_t')
        self.assertEqual(declaration_1.parameters[2].name, 'wallet_handle')
        self.assertEqual(declaration_1.parameters[2].type, 'int32_t')
        self.assertEqual(declaration_1.parameters[3].name, 'submitter_did')
        self.assertEqual(declaration_1.parameters[3].type, 'const char *')
        self.assertEqual(declaration_1.parameters[4].name, 'request_json')
        self.assertEqual(declaration_1.parameters[4].type, 'const char *')
        callback = declaration_1.parameters[5]
        self.assertTrue(isinstance(callback, CallbackDeclaration))
        self.assertEqual(callback.return_type, 'void')
        self.assertEqual(len(callback.parameters), 3)
        self.assertEqual(callback.parameters[0].name, 'xcommand_handle')
        self.assertEqual(callback.parameters[0].type, 'int32_t')
        self.assertEqual(callback.parameters[1].name, 'err')
        self.assertEqual(callback.parameters[1].type, 'int32_t')
        self.assertEqual(callback.parameters[2].name, 'request_result_json')
        self.assertEqual(callback.parameters[2].type, 'const char*')

        declaration_2 = declarations[1]
        self.assertEqual(declaration_2.name, 'submit_request')
        self.assertEqual(declaration_2.return_type, 'int32_t')
        self.assertEqual(len(declaration_2.parameters), 4)
        self.assertEqual(declaration_2.parameters[0].name, 'command_handle')
        self.assertEqual(declaration_2.parameters[0].type, 'int32_t')
        self.assertEqual(declaration_2.parameters[1].name, 'pool_handle')
        self.assertEqual(declaration_2.parameters[1].type, 'int32_t')
        self.assertEqual(declaration_2.parameters[2].name, 'request_json')
        self.assertEqual(declaration_2.parameters[2].type, 'const char *')
        callback = declaration_2.parameters[3]
        self.assertTrue(isinstance(callback, CallbackDeclaration))
        self.assertEqual(callback.return_type, 'void')
        self.assertEqual(len(callback.parameters), 3)
        self.assertEqual(callback.parameters[0].name, 'xcommand_handle')
        self.assertEqual(callback.parameters[0].type, 'int32_t')
        self.assertEqual(callback.parameters[1].name, 'err')
        self.assertEqual(callback.parameters[1].type, 'int32_t')
        self.assertEqual(callback.parameters[2].name, 'request_result_json')
        self.assertEqual(callback.parameters[2].type, 'const char*')

        declaration_3 = declarations[2]
        self.assertEqual(declaration_3.name, 'sign_request')
        self.assertEqual(declaration_3.return_type, 'int32_t')
        self.assertEqual(len(declaration_3.parameters), 5)
        self.assertEqual(declaration_3.parameters[0].name, 'command_handle')
        self.assertEqual(declaration_3.parameters[0].type, 'int32_t')
        self.assertEqual(declaration_3.parameters[1].name, 'wallet_handle')
        self.assertEqual(declaration_3.parameters[1].type, 'int32_t')
        self.assertEqual(declaration_3.parameters[2].name, 'submitter_did')
        self.assertEqual(declaration_3.parameters[2].type, 'const char *')
        self.assertEqual(declaration_3.parameters[3].name, 'request_json')
        self.assertEqual(declaration_3.parameters[3].type, 'const char *')
        callback = declaration_3.parameters[4]
        self.assertTrue(isinstance(callback, CallbackDeclaration))
        self.assertEqual(callback.return_type, 'void')
        self.assertEqual(len(callback.parameters), 3)
        self.assertEqual(callback.parameters[0].name, 'xcommand_handle')
        self.assertEqual(callback.parameters[0].type, 'int32_t')
        self.assertEqual(callback.parameters[1].name, 'err')
        self.assertEqual(callback.parameters[1].type, 'int32_t')
        self.assertEqual(callback.parameters[2].name, 'signed_request_json')
        self.assertEqual(callback.parameters[2].type, 'const char*')

    def test_generate_c_proxy_string(self):
        expected_c_proxy_code = """
        int32_t indy_sign_request_proxy(void * f, int32_t command_handle, int32_t wallet_handle, const char * submitter_did, const char * request_json){
            int32_t (*func)(int32_t, int32_t, const char *, const char *, void (*)(int32_t, int32_t, const char *)) = f;
            return func(command_handle, wallet_handle, submitter_did, request_json, &signRequestCallback);
        }
        """

        c_proxy_code = Generator._generate_c_proxy_code(self.indy_function)
        c_proxy_code = re.sub(_WHITESPACE_PATT, '', c_proxy_code)
        expected_c_proxy_code = re.sub(_WHITESPACE_PATT, '', expected_c_proxy_code)

        self.assertEqual(expected_c_proxy_code, c_proxy_code)

    def test_generate_c_proxy_declaration_code(self):
        expected_c_proxy_declaration_code = "int32_t indy_sign_request_proxy(void * f, int32_t command_handle, int32_t wallet_handle, const char * submitter_did, const char * request_json);"

        c_proxy_declaration_code = Generator._generate_c_proxy_declaration_code(self.indy_function)

        self.assertEqual(c_proxy_declaration_code, expected_c_proxy_declaration_code)

    # Go code generation
    def test_generate_correct_result_struct_definition(self):
        expected_definition_code = """
        type signRequestResult struct {
            code int32
            signedRequestJson string
        }
        """
        expected_definition_code = re.sub(_WHITESPACE_PATT, '', expected_definition_code)

        actual_definition_code = Generator._generate_callback_result_struct_code(self.go_function)
        actual_definition_code = re.sub(_WHITESPACE_PATT, '', actual_definition_code)

        self.assertEqual(expected_definition_code, actual_definition_code)
