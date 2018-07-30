import unittest

from indygo_generator import header_scraping
from indygo_generator.types import FunctionParameter, CallbackDeclaration

from . import TEST_HEADER_FILE, TEST_FUNCTION_DECLARATION, TEST_PARAMETERS_STRING


class HeaderScrapingTests(unittest.TestCase):
    def test_scrape_header_file(self):
        declarations, type_map = header_scraping.scrape_header_file(TEST_HEADER_FILE)

        self.assertEqual(len(declarations), 3)
        declaration_1 = declarations[0]
        self.assertEqual(declaration_1.name, 'sign_and_submit_request')
        self.assertEqual(declaration_1.return_type, 'indy_error_t')
        self.assertEqual(len(declaration_1.parameters), 6)
        declaration_2 = declarations[1]
        self.assertEqual(declaration_2.name, 'submit_request')
        self.assertEqual(declaration_2.return_type, 'indy_error_t')
        self.assertEqual(len(declaration_2.parameters), 4)
        declaration_3 = declarations[2]
        self.assertEqual(declaration_3.name, 'sign_request')
        self.assertEqual(declaration_3.return_type, 'indy_error_t')
        self.assertEqual(len(declaration_3.parameters), 5)

        self.assertEqual(len(type_map), 7)
        self.assertEqual(type_map['indy_u8_t'], 'uint8_t')
        self.assertEqual(type_map['indy_u32_t'], 'uint32_t')
        self.assertEqual(type_map['indy_i32_t'], 'int32_t')
        self.assertEqual(type_map['indy_handle_t'], 'int32_t')
        self.assertEqual(type_map['indy_bool_t'], 'unsigned int')
        self.assertEqual(type_map['indy_i64_t'], 'long long')
        self.assertEqual(type_map['indy_u64_t'], 'unsigned long long')

    def test_parse_function_declaration(self):
        function_declaration = header_scraping.parse_indy_function_declaration(TEST_FUNCTION_DECLARATION)

        self.assertEqual(function_declaration.name, 'sign_request')
        self.assertEqual(function_declaration.return_type, 'indy_error_t')
        self.assertEqual(len(function_declaration.parameters), 5)

    def test_parse_function_parameters(self):
        parameters = header_scraping._parse_function_parameters(TEST_PARAMETERS_STRING)

        self.assertEqual(len(parameters), 5)
        self.assertTrue(isinstance(parameters[0], FunctionParameter))
        self.assertEqual(parameters[0].name, 'command_handle')
        self.assertEqual(parameters[0].type, 'indy_handle_t')
        self.assertTrue(isinstance(parameters[1], FunctionParameter))
        self.assertEqual(parameters[1].name, 'wallet_handle')
        self.assertEqual(parameters[1].type, 'indy_handle_t')
        self.assertTrue(isinstance(parameters[2], FunctionParameter))
        self.assertEqual(parameters[2].name, 'submitter_did')
        self.assertEqual(parameters[2].type, 'const char *')
        self.assertTrue(isinstance(parameters[3], FunctionParameter))
        self.assertEqual(parameters[3].name, 'request_json')
        self.assertEqual(parameters[3].type, 'const char *')
        callback = parameters[4]
        self.assertTrue(isinstance(callback, CallbackDeclaration))
        self.assertEqual(callback.return_type, 'void')
        self.assertEqual(len(callback.parameters), 3)
        self.assertTrue(isinstance(callback.parameters[0], FunctionParameter))
        self.assertEqual(callback.parameters[0].name, 'xcommand_handle')
        self.assertEqual(callback.parameters[0].type, 'indy_handle_t')
        self.assertTrue(isinstance(callback.parameters[1], FunctionParameter))
        self.assertEqual(callback.parameters[1].name, 'err')
        self.assertEqual(callback.parameters[1].type, 'indy_error_t')
        self.assertTrue(isinstance(callback.parameters[2], FunctionParameter))
        self.assertEqual(callback.parameters[2].name, 'signed_request_json')
        self.assertEqual(callback.parameters[2].type, 'const char*')

    def test_split_params(self):
        param_strings = header_scraping._split_parameter_string(TEST_PARAMETERS_STRING)

        self.assertEqual(len(param_strings), 5)
        self.assertEqual(param_strings[0], 'indy_handle_t command_handle')
        self.assertEqual(param_strings[1], 'indy_handle_t wallet_handle')
        self.assertEqual(param_strings[2], 'const char * submitter_did')
        self.assertEqual(param_strings[3], 'const char * request_json')
        self.assertEqual(param_strings[4], 'void (*cb)(indy_handle_t xcommand_handle, indy_error_t err, const char* signed_request_json)')
