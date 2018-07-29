import unittest
from unittest.mock import patch, Mock

from indygo_generator.generator import Generator
from indygo_generator.function import CallbackDeclaration

from . import TEST_HEADER_FILE


class GeneratorTests(unittest.TestCase):
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