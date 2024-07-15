from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from microservices_utils.tools.logger import internal_logger

from microservices_utils.tools.singleton import Singleton
from microservices_utils.tools.errors.project_exception import ProjectException

logger = internal_logger.get_logger()

class Sms(Singleton):
    client = None
    verify_sid = None

    def __init__(self, account_sid, auth_token, verify_sid):
        Sms.client = Client(account_sid, auth_token)
        Sms.verify_sid = verify_sid

    @classmethod
    def send_code(cls, mobile_phone: str):
        try:
            formatted_phone = cls.__format_phone(mobile_phone)
            cls.client.verify.services(cls.verify_sid).verifications.create(to=formatted_phone,
                                                                            channel='sms',
                                                                            locale='en')
        except TwilioRestException as exc:
            cls.__raise_twilio_exc(exc)

    @classmethod
    def is_valid_code(cls, mobile_phone: str, code: str):
        try:
            logger.info('01 ========================================================================')
            formatted_phone = cls.__format_phone(mobile_phone)
            verification_check = cls.client.verify.services(cls.verify_sid).verification_checks.create(
                to=formatted_phone,
                code=code)
            logger.info('========================================================================')
            logger.info(type(verification_check))
            logger.info('========================================================================')

        except TwilioRestException as exc:
            cls.__raise_twilio_exc(exc)
        else:
            logger.info('?????? ========================================================================')
            logger.info(type(verification_check))
            logger.info('========================================================================')
            return verification_check.status == 'approved'

    @classmethod
    def __format_phone(cls, mobile_phone: str) -> str:
        formatted_phone = cls.client.lookups.phone_numbers(mobile_phone).fetch(country_code='US')
        if formatted_phone.country_code in {'US', 'ES', 'MX', 'PR'}:
            return formatted_phone.phone_number
        else:
            raise ProjectException(tag='INVALID_MOBILE_PHONE')

    @classmethod
    def __raise_twilio_exc(cls, exc):
        if 'PhoneNumbers' in exc.msg and 'was not found' in exc.msg:
            raise ProjectException(tag='INVALID_MOBILE_PHONE',
                                   message='The mobile phone is not valid, try adding the country code')
        elif 'VerificationCheck' in exc.uri and 'was not found' in exc.msg:
            raise ProjectException(tag='VERIFICATION_SMS_NOT_FOUND')
        elif 'Max check attempts reached' in exc.msg:
            raise ProjectException(tag='MAX_ATTEMPTS_REACHED')
        else:
            raise ProjectException(message=f'TWILIO error: {exc.msg}')

    @classmethod
    def validation(cls, phone: str):
        """
        Format lookups are free and allow you to identify and adjust international phone numbers into E.164 format for
        optimal message deliverability.

        Carrier lookups cost $0.005 per lookup and allow you to identify both the phone type (mobile, landline or VoIP)
        and the carrier behind the phone number.

        Caller name lookups $0.01

        """
        phone_number = cls.client.lookups.phone_numbers(phone).fetch(type=['carrier'])

        return phone_number.carrier

    @classmethod
    def fetch_verification(cls, verification_sid):
        return cls.client.verify.services(cls.verify_sid).verifications(verification_sid).fetch()
