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

import uuid

from django.db.models import Avg
from django.db.models import Count
from django.db.models import Q
from django.db.models import F, Func
from django.contrib.contenttypes.models import ContentType

from taiga.projects.history.models import HistoryEntry
from taiga.projects.milestones.models import Milestone
from taiga.projects.models import Project
from taiga.projects.notifications.models import Watched
from taiga.projects.userstories.models import UserStory
from taiga.telemetry.models import InstanceTelemetry
from taiga.users.models import User


def get_or_create_instance_id():
    instance = InstanceTelemetry.objects.first()
    if not instance:
        instance = InstanceTelemetry.objects.create(
            instance_id=uuid.uuid4().hex
        )

    return instance.instance_id


def generate_platform_data():
    total_uss = UserStory.objects.count()

    platform_data = {
        # number of projects
        'tt_projects': Project.objects.count(),

        # number of private projects
        'tt_projects_private': Project.objects.filter(
                is_private=True
            ).count(),

        # number of public projects
        'tt_projects_public': Project.objects.filter(
                is_private=False
            ).count(),

        # number of projects with scrum active and kanban inactive
        'tt_projects_only_scrum': Project.objects.filter(
                is_backlog_activated=True, is_kanban_activated=False
            ).count(),

        # number of projects with both scrum and kanban active
        'tt_projects_kanban_scrum': Project.objects.filter(
                is_backlog_activated=True, is_kanban_activated=True
            ).count(),

        # number of projects with none scrum and kanban active
        'tt_projects_no_kanban_no_scrum': Project.objects.filter(
                is_backlog_activated=False, is_kanban_activated=False
            ).count(),

        # number of projects with kaban active and scrum inactive
        'tt_projects_only_kanban': Project.objects.filter(
                is_backlog_activated=False, is_kanban_activated=True
            ).count(),

        # number of projects with kaban active and at least 1 swimlane
        'tt_projects_swimlanes_active_kanban': Project.objects.annotate(
                total_swimlanes=Count('swimlanes')
            ).filter(
                total_swimlanes__gte=1, is_kanban_activated=True
            ).count(),

        # number of projects with kaban inactive and at least 1 swimlane
        'tt_projects_swimlanes_inactive_kanban': Project.objects.annotate(
                total_swimlanes=Count('swimlanes')
            ).filter(
                total_swimlanes__gte=1, is_kanban_activated=True
            ).count(),

        # number of projects with issues active
        'tt_projects_issues': Project.objects.filter(
                is_issues_activated=True
            ).count(),

        # number of projects with epics active
        'tt_projects_epics': Project.objects.filter(
                is_epics_activated=True
            ).count(),

        # number of projects with wiki active
        'tt_projects_wiki': Project.objects.filter(
                is_wiki_activated=True
            ).count(),

        # number of projects using custom fields
        'tt_projects_custom_fields': Project.objects.annotate(
                total_custom_fields=Count('epiccustomattributes', distinct=True) + \
                                    Count('issuecustomattributes', distinct=True) + \
                                    Count('taskcustomattributes', distinct=True) + \
                                    Count('userstorycustomattributes', distinct=True)
            ).exclude(
                total_custom_fields=0
            ).count(),

        # number of users
        'tt_users': User.objects.count(),

        # number of active users
        'tt_users_active': User.objects.filter(
                is_active=True
            ).count(),

        # average of epics in projects with module epics active
        'tt_avg_epics_project': Project.objects.filter(
                is_epics_activated=True
            ).annotate(
                total_epics=Count('epics')
            ).aggregate(
                avg_epics_project=Avg('total_epics')
            )['avg_epics_project'],

        # average of userstories in projects with module scrum or kanban active
        'tt_avg_uss_project': Project.objects.filter(
                Q(is_kanban_activated=True) | Q(is_backlog_activated=True)
            ).annotate(
                total_user_stories=Count('user_stories')
            ).aggregate(
                avg_uss_project=Avg('total_user_stories')
            )['avg_uss_project'],

        # average of isues in projects with module issues active
        'tt_avg_issues_project': Project.objects.filter(
                is_issues_activated=True
            ).annotate(
                total_issues=Count('issues')
            ).aggregate(
                avg_issues_project=Avg('total_issues')
            )['avg_issues_project'],

        # average of swimlanes in projects with kanban and at least one swimlane
        'tt_avg_swimlanes_project': Project.objects.annotate(
                total_swimlanes=Count('swimlanes')
            ).filter(
                total_swimlanes__gte=1, is_kanban_activated=True
            ).aggregate(
                avg_swimlanes_project=Avg('total_swimlanes')
            )['avg_swimlanes_project'],

        # average of tags per project
        'tt_avg_tags_project': Project.objects.annotate(
                total_tags=Func(F('tags_colors'), function='CARDINALITY')
            ).aggregate(
                avg_tags_project=Avg('total_tags')
            )['avg_tags_project'],

        # average of custom fields per project
        'tt_avg_custom_fields_project': Project.objects.annotate(
                total_custom_fields=Count('epiccustomattributes', distinct=True) + \
                                    Count('issuecustomattributes', distinct=True) + \
                                    Count('taskcustomattributes', distinct=True) + \
                                    Count('userstorycustomattributes', distinct=True)
            ).exclude(
                total_custom_fields=0
            ).aggregate(
                avg_custom_fields_project=Avg('total_custom_fields')
            )['avg_custom_fields_project'],

        # average of members per project
        'tt_avg_members_project': Project.objects.annotate(
                total_members=Count('members')
            ).aggregate(
                avg_members_project=Avg('total_members')
            )['avg_members_project'],

        # average of roles per project
        'tt_avg_roles_project': Project.objects.annotate(
                total_roles=Count('roles')
            ).aggregate(
                avg_roles_project=Avg('total_roles')
            )['avg_roles_project'],

        # percent of user stories assigned
        'tt_percent_uss_assigned': _get_tt_percent_uss_assigned(total_uss),

        # percent of user stories watched
        'tt_percent_uss_watching': _get_tt_percent_uss_watched(total_uss),

        # percent of user stories with at least one comment
        'tt_percent_uss_comments_gte_1': HistoryEntry.objects.filter(
                key__startswith='userstories.userstory:',
                comment__isnull=False
            ).order_by(
                'key'
            ).distinct(
                'key'
            ).count(),

        # average of sprints in projects with backlog activated
        'tt_avg_sprints_project': Project.objects.annotate(
                total_sprints=Count('milestones')
            ).filter(
                total_sprints__gte=1, is_backlog_activated=True
            ).aggregate(
                avg_sprints_project=Avg('total_sprints')
            )['avg_sprints_project'],

        # average of uss per sprint
        'tt_avg_uss_sprint': Milestone.objects.annotate(
                total_user_stories=Count('user_stories')
            ).aggregate(
                avg_uss_sprint=Avg('total_user_stories')
            )['avg_uss_sprint'],

        # TODO: number of logins

        # number of edits
        'tt_edits': HistoryEntry.objects.filter(
            created_at__day=datetime.datetime.today().day
        ).count()

        # number of new US
        'tt_new_user_stories': UserStory.objects.filter(
            created_date__day=datetime.datetime.today().day
        ).count()

        # number of closed US
        'tt_finished_user_stories': UserStory.objects.filter(
            finish_date__day=datetime.datetime.today().day
        ).count()

    }

    return platform_data


def generate_system_data():
    system_data = {
        # 'IP y MOVIDAS'
        # Version of the platform
        # Running since
        # país
    }

    return system_data


def _get_tt_percent_uss_assigned(total_uss):
    assigned_uss = UserStory.objects.filter(assigned_users__isnull=False).count()
    return assigned_uss * 100 / total_uss


def _get_tt_percent_uss_watched(total_uss):
    content_type = ContentType.objects.get(model='userstory')
    watched_uss = Watched.objects.filter(content_type=content_type).distinct('object_id').count()
    return watched_uss * 100 / total_uss
