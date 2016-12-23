"""
Settings package initialization.
"""

import os

# Ensure development settings are not used in testing and production
if not os.getenv('CI') and not os.getenv('HEROKU'):
    # load and set environment variables from '.env.yml' with django-envie
    from django_envie.workroom import convertfiletovars
    convertfiletovars()

    from development import *

if os.getenv('HEROKU') is not None:
    from production import *
