# import inspect
# import json
# import logging
# import pytz

# from datetime import datetime
# from django.conf import settings
# TZ = pytz.timezone(settings.TIME_ZONE)


# def ensure_json_safe(obj):
#     """Ensure an object is serialized to be json-safe"""
#     if hasattr(obj, '__dict__'):
#         return repr(obj)
#     elif isinstance(obj, datetime):
#         return obj.astimezone(TZ).isoformat()
#     else:
#         return unicode(obj)


# class JsonLogFormatter(logging.Formatter):

#     def format(self, record):
#         call_stack =
