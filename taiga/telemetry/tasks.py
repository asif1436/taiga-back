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

from django.conf import settings
import rudder_analytics

from taiga.celery import app
from taiga.telemetry import services



@app.task
def send_telemetry():
    rudder_analytics.write_key = settings.RUDDER_WRITE_KEY
    rudder_analytics.data_plane_url = settings.DATA_PLANE_URL

    instance_id = services.get_or_create_instance_id()
    event = 'Daily telemetry'

    properties = {
        **services.generate_platform_data(),
        **services.generate_system_data(),
    }

    rudder_analytics.track(
        user_id=instance_id,
        event=event,
        properties=properties
    )
