# Copyright (c) 2017 University of Central Florida - Center for Distributed Learning

import os

# Using a placeholder for environment variables.
# If not found in the environment, it will default to the local value, which is set in
# the second parameter. Example:
# os.environ.get("ENVIRONMENT_KEY", "LOCAL_VALUE")
# This makes it a bit easier to use one file for local and environment deployment.

# Declare your consumer key and shared secret. If you end
# up having multiple consumers, you may want to add separate
# key/secret sets for them.
CONSUMER_KEY = os.environ.get("CONSUMER_KEY", "CHANGEME")
SHARED_SECRET = os.environ.get("SHARED_SECRET", "CHANGEME")

# Configuration for LTI
PYLTI_CONFIG = {
    'consumers': {
        CONSUMER_KEY: {
            "secret": SHARED_SECRET
        }
        # Feel free to add more key/secret pairs for other consumers.
    },
    'roles': {
        # Maps values sent in the lti launch value of "roles" to a group
        # Allows you to check LTI.is_role('admin') for your user
        'admin': ['Administrator', 'urn:lti:instrole:ims/lis/Administrator'],
        'lecturer': ['Instructor', 'urn:lti:instrole:ims/lis/Instructor'],
        'student': ['Student', 'urn:lti:instrole:ims/lis/Student']
    }
}

# Secret key used for Flask sessions, etc. Must stay named 'secret_key'.
# Can be any randomized string, recommend generating one with os.urandom(24)
secret_key = os.environ.get("SECRET_FLASK", "CHANGEME")

# Application Logging
LOG_FILE = 'error.log'
LOG_FORMAT = '%(asctime)s [%(levelname)s] {%(filename)s:%(lineno)d} %(message)s'
LOG_LEVEL = 'INFO'
LOG_MAX_BYTES = 1024 * 1024 * 5  # 5 MB
LOG_BACKUP_COUNT = 1

# Config object settings
# See config.py other environments and options
configClass = 'config.DevelopmentConfig'

# Settings for RAGE
#
RAGE_GAME_HOST = os.environ.get("RAGE_HOST", 'http://127.0.0.1:3000/api/proxy/gleaner/collector')
RAGE_TRACKER_ID = os.environ.get('RAGE_TRACKER', '')
RAGE_GAME_ID = os.environ.get('RAGE_GAME_ID', '')
RAGE_GAME_VERSION_ID = os.environ.get('RAGE_GAME_VERSION_ID', '')
RAGE_DEFAULT_STUDENT_PASSWORD = os.environ.get('RAGE_DEFAULT_STUDENT_PASSWORD', 'CHANGEME')
RAGE_USERNAME = os.environ.get('RAGE_USERNAME', '')
RAGE_PASSWORD = os.environ.get('RAGE_PASSWORD', '')
