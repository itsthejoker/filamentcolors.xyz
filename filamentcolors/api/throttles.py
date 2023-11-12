from rest_framework.throttling import AnonRateThrottle


class BurstRateThrottle(AnonRateThrottle):
    scope = 'burst'

class SustainedRateThrottle(AnonRateThrottle):
    scope = 'sustained'