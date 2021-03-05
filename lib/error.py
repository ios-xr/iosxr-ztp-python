from enum import Enum
class _AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class ErrorCode(_AutoNumber):
    ###### Generic errors start ######
    INVALID_RESPONSE = ()
    INVALID_INPUT = ()
    INVALID_DATA = ()
    INVALID_COMMAND = ()
    COMMAND_NOT_SPECIFIED = ()
    INVALID_INPUT_TYPE = ()
    INVALID_CA_CERTIFICATE =()
    ###### Generic errors end ######

    # Config Errors
    INVALID_CONFIG_PATH = ()

    # HTTP Errors
    HTTP_POST_REQUEST_FAILED = ()
    HTTP_GET_REQUEST_FAILED = ()
    HTTP_OPERATION_TIMEDOUT = ()
    DOWNLOAD_FAILED = ()
    DOWNLOAD_FAILED_MD5_MISMATCH = ()


    # Setns Errors
    FAILED_READING_FD = ()
    FAILED_SWITCHING_NS = ()


    def __str__(self):
        return str(self.name).lower().replace('_', '-')

    def __repr__(self):
        return str(self)