# -*- coding: utf-8 -*-
# Copyright (C) 2014-2017 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2017 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014-2017 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014-2017 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .common import *
import os

#########################################
## GENERIC
#########################################

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': '5432',
    }
}

SECRET_KEY = os.getenv('TAIGA_SECRET_KEY')
TAIGA_URL = f"{ os.getenv('TAIGA_SITES_SCHEME') }://{ os.getenv('TAIGA_SITES_DOMAIN') }"
MEDIA_URL = f"{ TAIGA_URL }/media/"
STATIC_URL = f"{ TAIGA_URL }/static/"
SITES = {
    "api": {"domain": f"{ os.getenv('TAIGA_SITES_DOMAIN') }", "scheme": f"{ os.getenv('TAIGA_SITES_SCHEME') }", "name": "api"},
    "front": {"domain": f"{ os.getenv('TAIGA_SITES_DOMAIN') }", "scheme": f"{ os.getenv('TAIGA_SITES_SCHEME') }", "name": "front"}
}


#########################################
## EMAIL
#########################################
# https://docs.djangoproject.com/en/3.1/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'system@taiga.io')
ENABLE_EMAIL = os.getenv('ENABLE_EMAIL', 'False') == 'True'
CHANGE_NOTIFICATIONS_MIN_INTERVAL = 60  # seconds
SEND_BULK_EMAIL = True

if ENABLE_EMAIL:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
    EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'user')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'password')


#########################################
## EVENTS
#########################################
EVENTS_PUSH_BACKEND = "taiga.events.backends.rabbitmq.EventsPushBackend"
EVENTS_PUSH_BACKEND_OPTIONS = {
    "url": f"amqp://{ os.getenv('RABBITMQ_USER') }:{ os.getenv('RABBITMQ_PASS') }@taiga-events-rabbitmq:5672/taiga"
}


#########################################
## TAIGA ASYNC
#########################################
CELERY_ENABLED = True
from kombu import Queue  # noqa

CELERY_BROKER_URL = f"amqp://{ os.getenv('RABBITMQ_USER') }:{ os.getenv('RABBITMQ_PASS') }@taiga-async-rabbitmq:5672/taiga"
CELERY_RESULT_BACKEND = None # for a general installation, we don't need to store the results
CELERY_ACCEPT_CONTENT = ['pickle', ]  # Values are 'pickle', 'json', 'msgpack' and 'yaml'
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_TIMEZONE = 'Europe/Madrid'
CELERY_TASK_DEFAULT_QUEUE = 'tasks'
CELERY_QUEUES = (
    Queue('tasks', routing_key='task.#'),
    Queue('transient', routing_key='transient.#', delivery_mode=1)
)
CELERY_TASK_DEFAULT_EXCHANGE = 'tasks'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'task.default'


#########################################
## CONTRIBS
#########################################
INSTALLED_APPS += [
    "taiga_contrib_slack",
    "taiga_contrib_github_auth",
    "taiga_contrib_gitlab_auth"
]

GITHUB_API_CLIENT_ID = os.getenv('GITHUB_API_CLIENT_ID')
GITHUB_API_CLIENT_SECRET = os.getenv('GITHUB_API_CLIENT_SECRET')

GITLAB_API_CLIENT_ID = os.getenv('GITLAB_API_CLIENT_ID')
GITLAB_API_CLIENT_SECRET = os.getenv('GITLAB_API_CLIENT_SECRET')
GITLAB_URL = os.getenv('GITLAB_URL')


#########################################
## TELEMETRY
#########################################
ENABLE_TELEMETRY = os.getenv('ENABLE_TELEMETRY', 'True') == 'True'
RUDDER_WRITE_KEY = '1kmTTxJoSmaZNRpU1uORpyZ8mqv'
