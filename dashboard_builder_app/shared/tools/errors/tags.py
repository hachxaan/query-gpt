ERRORS = {
    'TRANSFER_NOT_FOUND': {
        'code': 404,
        'message': 'Transfer not found',
    },
    'MALFORMED_REQUEST': {
        'code': 400,
        'message': 'Bad Request',
    },
    'ACCESS_RESTRICTED': {
        'code': 400,
        'message': 'Restricted Access',
    },
    'MISSING_FIELD': {
        'code': 422,
        'message': 'Unprocessable Entity',
    },
    'MISSING_FILE': {
        'code': 422,
        'message': 'Unprocessable Entity, file is required with correct name',
    },
    'WRONG_FORMAT_FILE': {
        'code': 422,
        'message': 'Unprocessable Entity, file has wrong format',
    },
    'INTERNAL_ERROR': {
        'code': 500,
        'message': 'Internal error',
    },
    'NOT_IMPLEMENTED': {
        'code': 501,
        'message': 'Not implemented',
    },
    'NOT_AUTH': {'code': 401, 'message': 'Not authorized user'},
    'FORBIDDEN': {'code': 403, 'message': 'Forbidden'},
    'EXISTING_EMAIL': {'code': 409, 'message': 'Email already exists'},
    'ALREADY_EXISTING': {'code': 409, 'message': 'already exists'},
    'ALREADY_RECURRENT_CREDIT': {
        'code': 409,
        'message': 'Recurrent credit already active',
    },
    'EXISTING_NAME': {'code': 409, 'message': 'Name already exists'},
    'TIPS_CREDIT_UNAVAILABLE': {
        'code': 400,
        'message': 'Maximun credit unavailable for the user',
    },
    'WRONG_CREDENTIALS': {'code': 401, 'message': 'Wrong email or password'},
    'SMS_CODE_NEEDED': {
        'code': 400,
        'message': 'The sms code is not present in header',
    },
    'SMS_CODE_NOT_YET_VERIFIED': {
        'code': 400,
        'message': 'The sms code is not yet verified on the endpoint api/sms/<sms_code>',
    },
    'INVALID_CODE': {'code': 422, 'message': 'The code is not valid'},
    'WRONG_PRODUCT_TYPE': {
        'code': 422,
        'message': 'The product code type is not valid',
    },
    'REQUIRED_PRODUCT_CODE': {
        'code': 400,
        'message': 'The product code type is not valid',
    },
    'PRODUCT_NOT_FOUND': {
        'code': 404,
        'message': 'Product not found',
    },
    'USER_NOT_FOUND': {
        'code': 404,
        'message': 'User not found',
    },
    'CUSTOMER_NOT_FOUND': {
        'code': 404,
        'message': 'Customer not found',
    },
    'COMPANY_NOT_FOUND': {
        'code': 404,
        'message': 'Company not found',
    },
    'COMPANY_TIPS_NOT_FOUND': {
        'code': 404,
        'message': 'Company tips not found',
    },
    'CREDIT_NOT_FOUND': {
        'code': 404,
        'message': 'Credit not found',
    },
    'RECURRENT_CREDIT_NOT_FOUND': {
        'code': 404,
        'message': 'Recurrent credit not found',
    },
    'NOT_FOUND': {'code': 404, 'message': 'Not found'},
    'EMAIL_NOT_FOUND': {'code': 401, 'message': 'email not found'},
    'CREDIT_CARD_NOT_FOUND': {'code': 404, 'message': 'Credit card not found'},
    'CREDIT_CARD_INACTIVE': {'code': 400, 'message': 'Credit card not found'},
    'WRONG_TOKEN': {'code': 401, 'message': 'The token is invalid'},
    'EXPIRED_TOKEN': {'code': 401, 'message': 'The token has expired'},
    'CONFIRMATION_TOKEN_EXPIRED': {
        'code': 401,
        'message': 'The confirmation token time has expired',
    },
    'METHOD_NOT_FOUND': {'code': 405, 'message': 'Method not allowed'},
    'EMAIL_NOT_SENT': {'code': 500, 'message': 'email not sent'},
    'BAD_GATEWAY': {'code': 502, 'message': 'Bad Gateway'},
    'RESOURCE_NOT_FOUND': {
        'code': 404,
        'message': 'Resource not found',
    },
    'SECTION_CANT_DELETE': {
        'code': 400,
        'message': 'Section has nested categories',
    },
    'WRONG_ZIP_CODE': {
        'code': 410,
        'message': 'Invalid zip code',
    },
    'CONFIRMED_EMAIL': {
        'code': 410,
        'message': 'Wrong user confirmed email',
    },
    'TERMS_CONDITIONS': {
        'code': 410,
        'message': 'Wrong user terms and conditions',
    },
    # BANK ACCOUNT
    'BANK_ACCOUNT_NOT_FOUND': {
        'code': 404,
        'message': 'Bank account not found',
    },
    'INACTIVE_BANK_ACCOUNT': {'code': 400, 'message': 'Inactive Bank account'},
    # ATRIUM ERRORS
    'ATRIUM_SERVICE_ERROR': {
        'code': 503,
    },
    'ATRIUM_USER_ALREADY_CREATED': {
        'code': 409,
        'message': 'User on atrium already exists',
    },
    'ATRIUM_USER_NOT_EXISTS': {
        'code': 400,
        'message': 'User is not connected to atrium',
    },
    'ATRIUM_NOT_CONNECTED_ERROR_BANK': {
        'code': 400,
        'message': 'User not yet connected with the bank',
    },
    # PAYROLL CREDIT
    'PAYROLL_CREDIT_UNAVAILABLE': {
        'code': 400,
        'message': 'Maximun credit unavailable for the user',
    },
    'TIMECARD_UNAVAILABLE': {
        'code': 400,
        'message': 'Unavailable to updete user timecard',
    },
    # COMPANY USERS
    'ADMIN_PEO_IN_NO_PEO_COMPANY': {
        'code': 409,
        'message': 'PEO admins must belong to a PEO Company',
    },
    'INVALID_MOBILE_PHONE': {
        'code': 422,
        'message': 'The mobile phone is not valid',
    },
    'VERIFICATION_SMS_NOT_FOUND': {
        'code': 404,
        'message': 'Verification not found. Request an SMS first',
    },
    'NOT_ENOUGH_CASHBACK_BALANCE': {
        'code': 409,
        'message': 'User has not enough Cashback balance',
    },
    'MAX_ATTEMPTS_REACHED': {
        'code': 429,
        'message': 'Second factor auth. max. attempts reached',
    },
    'VIOLATES_NOT_NULL_CONSTRAIN': {
        'code': 409,
        'message': 'A field violates not-null constraint',
    },
    'CREDIT_LIMIT_EXCEEDED': {
        'code': 422,
        'message': 'The requested amount is higher than the credit limit',
    },
    'MIN_LIMIT': {
        'code': 422,
        'message': 'The requested credit that dont reach MIN limit',
    },
    'MAX_LIMIT': {
        'code': 422,
        'message': 'The requested credit that is higher than the MAX limit',
    },
    'CONECTION_NOT_PRESENT': {
        'code': 412,
        'message': 'Connection field does not exists',
    },
    'BADGE_NOT_FOUND': {
        'code': 404,
        'message': 'Badge not found',
    },
    # ISOLVED
    'PROVIDER_NOT_AUTH': {
        'code': 400,
        'message': 'Not valid employees provider credentials',
    },
    'OFFER_PROVIDER_UNKNOWN': {
        'code': 500,
        'message': 'The offer is not from a known provider',
    },
    'INVALID_FEE': {'code': 422, 'message': 'The fee is not valid'},
    "CONNECTION_ERROR": {
        'code': 502,
        'message': 'Failed to establish a new connection',
    },
    'TABAPAY_ERROR': {'code': 400, 'message': 'Tabapay error'},
    'SOLID_ERROR': {'code': 400, 'message': 'Solid error'},
    'INACTIVE_COMPANY': {'code': 400, 'message': 'Inactive company'},
    'INACTIVE_USER': {'code': 400, 'message': 'Inactive user'},
    'DEDUCTION_ERROR': {'code': 500, 'message': ''},
    'MALFORMED_USER': {'code': 500, 'message': ''},
    'OUTDATED_VERSION': {
        'code': 401,
        'message': 'New version available, please update app to the newest version to continue.',
    }
}
