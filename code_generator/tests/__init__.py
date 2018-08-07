TEST_HEADER_FILE = """
#ifndef __indy__ledger_included__
#define __indy__ledger_included__

#include "indy_mod.h"
#include "indy_types.h"

#ifdef __cplusplus
extern "C" {
#endif
    
    /// Signs and submits request message to validator pool.
    ///
    /// Adds submitter information to passed request json, signs it with submitter
    /// sign key (see wallet_sign), and sends signed request message
    /// to validator pool (see write_request).
    ///
    /// #Params
    /// command_handle: command handle to map callback to caller context.
    /// pool_handle: pool handle (created by open_pool_ledger).
    /// wallet_handle: wallet handle (created by open_wallet).
    /// submitter_did: Id of Identity stored in secured Wallet.
    /// request_json: Request data json.
    /// cb: Callback that takes command result as parameter.
    ///
    /// #Returns
    /// Request result as json.
    ///
    /// #Errors
    /// Common*
    /// Wallet*
    /// Ledger*
    /// Crypto*
    
    extern indy_error_t indy_sign_and_submit_request(indy_handle_t command_handle,
                                                     indy_handle_t pool_handle,
                                                     indy_handle_t wallet_handle,
                                                     const char *  submitter_did,
                                                     const char *  request_json,

                                                     void           (*cb)(indy_handle_t xcommand_handle,
                                                                          indy_error_t  err,
                                                                          const char*   request_result_json)
                                                     );
    
    /// Publishes request message to validator pool (no signing, unlike sign_and_submit_request).
    ///
    /// The request is sent to the validator pool as is. It's assumed that it's already prepared.
    ///
    /// #Params
    /// command_handle: command handle to map callback to caller context.
    /// pool_handle: pool handle (created by open_pool_ledger).
    /// request_json: Request data json.
    /// cb: Callback that takes command result as parameter.
    ///
    /// #Returns
    /// Request result as json.
    ///
    /// #Errors
    /// Common*
    /// Ledger*
    
    extern indy_error_t indy_submit_request(indy_handle_t command_handle,
                                            indy_handle_t pool_handle,
                                            const char *  request_json,

                                            void           (*cb)(indy_handle_t xcommand_handle,
                                                                 indy_error_t  err,
                                                                 const char*   request_result_json)
                                           );


    /// Signs request message.
    ///
    /// Adds submitter information to passed request json, signs it with submitter
    /// sign key (see wallet_sign).
    ///
    /// #Params
    /// command_handle: command handle to map callback to caller context.
    /// wallet_handle: wallet handle (created by open_wallet).
    /// submitter_did: Id of Identity stored in secured Wallet.
    /// request_json: Request data json.
    /// cb: Callback that takes command result as parameter.
    ///
    /// #Returns
    /// Signed request json.
    ///
    /// #Errors
    /// Common*
    /// Wallet*
    /// Ledger*
    /// Crypto*

    extern indy_error_t indy_sign_request(indy_handle_t command_handle,
                                         indy_handle_t  wallet_handle,
                                         const char *   submitter_did,
                                         const char *   request_json,

                                         void           (*cb)(indy_handle_t xcommand_handle,
                                                              indy_error_t  err,
                                                              const char*   signed_request_json)
                                         );
                                         
    typedef uint8_t       indy_u8_t;
    typedef uint32_t      indy_u32_t;
    typedef int32_t       indy_i32_t;
    typedef int32_t       indy_handle_t;
    typedef unsigned int  indy_bool_t;
    typedef long long     indy_i64_t;
    typedef unsigned long long     indy_u64_t;



"""

TEST_FUNCTION_DECLARATION = """
indy_error_t indy_sign_request(indy_handle_t command_handle,
                               indy_handle_t  wallet_handle,
                               const char *   submitter_did,
                               const char *   request_json,

                               void           (*cb)(indy_handle_t xcommand_handle,
                                                    indy_error_t  err,
                                                    const char*   signed_request_json)
                               );
"""


TEST_COMPLEX_FUNCTION_DECLARATION = """
indy_error_t indy_issuer_create_and_store_revoc_reg(indy_handle_t command_handle,
                                                    indy_handle_t wallet_handle,
                                                    const char *  issuer_did,
                                                    const char *  revoc_def_type,
                                                    const char *  tag,
                                                    const char *  cred_def_id,
                                                    const char *  config_json,
                                                    indy_handle_t tails_writer_handle,

                                                    void           (*cb)(indy_handle_t xcommand_handle,
                                                                         indy_error_t  err,
                                                                         const char*   revoc_reg_id,
                                                                         const char*   revoc_reg_def_json,
                                                                         const char*   revoc_reg_entry_json)
                                                    );
"""


TEST_PARAMETERS_STRING = 'indy_handle_t command_handle, indy_handle_t wallet_handle, const char * submitter_did, const char * request_json, void (*cb)(indy_handle_t xcommand_handle, indy_error_t err, const char* signed_request_json)'



TEST_C_FILE_CONTENT = """
include <stdint.h>


extern issuerCreateAndStoreRevocRegCallback(int32_t, int32_t, char *, char *, char *);


int32_t indy_issuer_create_and_store_revoc_reg_proxy(void * f, int32_t command_handle, int32_t wallet_handle, char * issuer_did, char * revoc_def_type, char * tag, char * cred_def_id, char * config_json, int32_t tails_writer_handle) {
    int32_t (*func)(int32_t, int32_t, char *, char *, char *, char *, char *, int32_t, void *) = f;
    return func(command_handle, wallet_handle, issuer_did, revoc_def_type, tag, cred_def_id, config_json, tails_writer_handle) = f;
}
"""