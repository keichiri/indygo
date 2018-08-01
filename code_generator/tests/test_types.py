import unittest

from indygo_generator.types import FunctionDeclaration, FunctionParameter, CallbackDeclaration, GoFunction


class FunctionTests(unittest.TestCase):
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
                ])
        ]
        self.simple_indy_function = FunctionDeclaration(name='sign_request',
                                                        return_type='int32_t',
                                                        parameters=params)

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
        self.complex_indy_function = FunctionDeclaration(name='sign_request',
                                                         return_type = 'int32_t',
                                                         parameters=params)

    def test_go_function_simple(self):
        go_function = GoFunction.create_from_indy_declaration(self.simple_indy_function)

        self.assertEqual(go_function.name, 'SignRequest')
        self.assertEqual(go_function.return_types, ['error'])
        params = go_function.parameters
        self.assertEqual(len(params), 3)
        param_0 = params[0]
        self.assertEqual(param_0.name, 'walletHandle')
        self.assertEqual(param_0.type, 'int32')
        param_1 = params[1]
        self.assertEqual(param_1.name, 'submitterDid')
        self.assertEqual(param_1.type, 'string')
        param_2 = params[2]
        self.assertEqual(param_2.name, 'requestJson')
        self.assertEqual(param_2.type, 'string')

        result_struct = go_function.result_struct
        self.assertEqual(len(result_struct.fields), 1)
        self.assertEqual(result_struct.fields[0].name, 'err')
        self.assertEqual(result_struct.fields[0].type, 'int32')

    def test_go_function_complex(self):
        go_function = GoFunction.create_from_indy_declaration(self.complex_indy_function)

        self.assertEqual(go_function.name, 'SignRequest')
        self.assertEqual(go_function.return_types, ['error', 'string'])
        params = go_function.parameters
        self.assertEqual(len(params), 3)
        param_0 = params[0]
        self.assertEqual(param_0.name, 'walletHandle')
        self.assertEqual(param_0.type, 'int32')
        param_1 = params[1]
        self.assertEqual(param_1.name, 'submitterDid')
        self.assertEqual(param_1.type, 'string')
        param_2 = params[2]
        self.assertEqual(param_2.name, 'requestJson')
        self.assertEqual(param_2.type, 'string')

        result_struct = go_function.result_struct
        self.assertEqual(len(result_struct.fields), 2)
        self.assertEqual(result_struct.fields[0].name, 'err')
        self.assertEqual(result_struct.fields[0].type, 'int32')
        self.assertEqual(result_struct.fields[1].name, 'signedRequestJson')
        self.assertEqual(result_struct.fields[1].type, 'string')
