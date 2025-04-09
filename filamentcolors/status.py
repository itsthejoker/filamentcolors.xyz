from rest_framework.status import *

HTTP_701_BAD_COLOR_CODE = 701
HTTP_702_MISSING_COLOR_CODE = 702
HTTP_703_UNPROCESSABLE_LAB_STR = 703

reasons = {
    HTTP_701_BAD_COLOR_CODE: "Invalid Color",
    HTTP_702_MISSING_COLOR_CODE: "Missing Color",
    HTTP_703_UNPROCESSABLE_LAB_STR: "Unprocessable LAB String",
}
