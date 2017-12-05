"""
Settings package initialization.
"""

import os


# Ensure development settings are not used in testing and production
if os.getenv('ENVIRONMENT') == "PRODUCTION":
    from production import *

elif os.getenv('HEROKU') == "TESTING":
    from testing import *

else:
    # load and set environment variables from '.env.yml' with django-envie
    from django_envie.workroom import convertfiletovars
    convertfiletovars()

    from development import *
