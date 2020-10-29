import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },

    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },

    'loggers': {
        'polls': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },

    'formatters': {
        'simple': {
            'format': '%(message)s at %(asctime)s',
        },
    },
}