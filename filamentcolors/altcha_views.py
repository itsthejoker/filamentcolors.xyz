import json

from altcha import create_challenge, ChallengeOptions, verify_solution
import bugsnag
from datetime import timedelta
from django.utils import timezone
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from filamentcolors import status
from filamentcolors.helpers import ErrorStatusResponse


def get_challenge(request: WSGIRequest):
    try:
        challenge = create_challenge(
            ChallengeOptions(
                hmac_key=settings.ALTCHA_HMAC_KEY,
                max_number=75000,
                expires=timezone.now() + timedelta(minutes=10),
            )
        )
        return JsonResponse(challenge.__dict__)
    except Exception as e:
        bugsnag.notify(e)
        return ErrorStatusResponse(
            status=status.HTTP_710_ALTCHA_UNABLE_TO_CREATE_CHALLENGE
        )


@csrf_exempt
def verify_challenge(request: WSGIRequest):
    payload = json.loads(request.body).get("payload")

    if not payload:
        return ErrorStatusResponse(status=status.HTTP_711_ALTCHA_MISSING_PAYLOAD)

    try:
        verified, err = verify_solution(payload, settings.ALTCHA_HMAC_KEY, True)
        if not verified:
            return ErrorStatusResponse(status=status.HTTP_712_ALTCHA_MALFORMED_PAYLOAD)

        return JsonResponse({"payload": payload}, status=200)

    except Exception as e:
        bugsnag.notify(e)
        return ErrorStatusResponse(status=status.HTTP_712_ALTCHA_MALFORMED_PAYLOAD)
