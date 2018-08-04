import unittest
import re
from unittest.mock import patch, Mock

from indygo_generator.generator import Generator
from indygo_generator.types import CallbackDeclaration, FunctionDeclaration, FunctionParameter, GoFunction, GoVariable

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
    def test_generate_correct_result_struct_declaration(self):
        expected_declaration_code = """
        type signRequestResult struct {
            err int32
            signedRequestJson string
        }
        """
        expected_declaration_code = re.sub(_WHITESPACE_PATT, '', expected_declaration_code)

        actual_definition_code = Generator._generate_callback_result_struct_code(self.go_function)
        actual_definition_code = re.sub(_WHITESPACE_PATT, '', actual_definition_code)

        self.assertEqual(expected_declaration_code, actual_definition_code)

    def test_generate_correct_callback_code(self):
        expected_callback_code = r"""
        //export signRequestCallback
        func signRequestCallback(xcommandHandle int32, err int32, signedRequestJson *C.char) {
            resCh, err := resolver.DeregisterCall(xcommandHandle)
            if err != nil {
		        log.Printf("ERROR: invalid handle in callback.\n")
		        return
	        }
	        
	        res := &signRequestResult{
		        err: err,
		        signedRequestJson: C.GoString(signedRequestJson),
	        }
	        resCh <- res
        }
        """
        expected_callback_code = re.sub(_WHITESPACE_PATT, '', expected_callback_code)

        actual_callback_code = Generator._generate_callback_code(self.go_function)
        actual_callback_code = re.sub(_WHITESPACE_PATT, '', actual_callback_code)

        self.assertEqual(expected_callback_code, actual_callback_code)

    def test_generate_correct_variable_setup_code_for_int32(self):
        variable = GoVariable(name='commandHandle', type='int32')

        expected_variable_setup_code = """
        var c_commandHandle C.int32_t
        c_commandHandle = C.int32_t(commandHandle)
        """
        expected_variable_setup_code = re.sub(_WHITESPACE_PATT, '', expected_variable_setup_code)

        cgo_var_name, actual_variable_setup_code = Generator._generate_variable_setup_code(variable)
        actual_variable_setup_code = re.sub(_WHITESPACE_PATT, '', actual_variable_setup_code)

        self.assertEqual(cgo_var_name, 'c_commandHandle')
        self.assertEqual(expected_variable_setup_code, actual_variable_setup_code)

    def test_generate_correct_variable_setup_code_for_string(self):
        variable = GoVariable(name='requestJson', type='string')

        expected_variable_setup_code = """
        var c_requestJson *C.char
        if requestJson != "" {
            c_requestJson = C.CString(requestJson)
            defer C.free(unsafe.Pointer(c_requestJson))
        }
        """
        expected_variable_setup_code = re.sub(_WHITESPACE_PATT, '', expected_variable_setup_code)

        cgo_var_name, actual_variable_setup_code = Generator._generate_variable_setup_code(variable)
        actual_variable_setup_code = re.sub(_WHITESPACE_PATT, '', actual_variable_setup_code)

        self.assertEqual(cgo_var_name, 'c_requestJson')
        self.assertEqual(expected_variable_setup_code, actual_variable_setup_code)

    def test_generate_correct_api_function_code(self):
        expected_api_function_code = """
        func SignRequest(walletHandle int32, submitterDid string, requestJson string) (string, error) {
            pointer, commandHandle, resCh, err := resolver.RegisterCall("indy_sign_request")
            if err != nil {
                return "", err
            }

            var c_walletHandle C.int32_t
            c_walletHandle = C.int32_t(walletHandle)

            var c_submitterDid *C.char
            if submitterDid != "" {
                c_submitterDid = C.CString(submitterDid)
                defer C.free(unsafe.Pointer(c_submitterDid))
            }

            var c_requestJson *C.char
            if requestJson != "" {
                c_requestJson = C.CString(requestJson)
                defer C.free(unsafe.Pointer(c_requestJson))
            }
            
            resCode := C.indy_sign_request_proxy(c_walletHandle, c_submitterDid, c_requestJson)
            if resCode != 0 {
                err = fmt.Errorf("Libindy returned code: %d", resCode)
                return "", err
            }
            
            _res := <- resCh
            res := _res.(*signRequestResult)
            
            if res.err != 0 {
                err = fmt.Errorf("Libindy returned code: %d", resCode)
                return "", err
            }
            
            return res.signedRequestJson, nil
        }
        """
        expected_api_function_code = re.sub(_WHITESPACE_PATT, '', expected_api_function_code)

        actual_api_function_code = Generator._generate_api_function_code(self.go_function)
        actual_api_function_code = re.sub(_WHITESPACE_PATT, '', actual_api_function_code)

        self.assertEqual(expected_api_function_code, actual_api_function_code)