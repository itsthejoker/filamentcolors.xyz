import os

# Route us to the correct settings file based on environment variables. Picked
# up this trick from a previous job. Also allows us to add a stage environment
# really easily.

env = os.environ.get('ENVIRONMENT', None)

if env == 'local':
    # noinspection PyUnresolvedReferences
    from filamentcolors.settings.local import *
else:
    # noinspection PyUnresolvedReferences
    from filamentcolors.settings.prod import *
