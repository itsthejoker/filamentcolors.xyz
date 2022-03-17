import logging
import os

# Route us to the correct settings file based on environment variables. Picked
# up this trick from a previous job. Also allows us to add a stage environment
# really easily.

env = os.environ.get("ENVIRONMENT", None)
logger = logging.getLogger("filamentcolors")

if env == "local":
    # noinspection PyUnresolvedReferences
    from filamentcolors.settings.local import *
elif os.path.exists("local_settings.py"):
    # Local override -- check for existence of local_settings.py and load it if possible
    logger.warning("Found local_settings.py -- loading and using!")
    from local_settings import *
else:
    from filamentcolors.settings.prod import *
