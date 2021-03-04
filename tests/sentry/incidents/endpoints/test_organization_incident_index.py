from exam import fixture
from datetime import timedelta

from django.utils import timezone
from sentry.api.serializers import serialize
from sentry.incidents.models import IncidentStatus
from sentry.incidents.logic import update_incident_status
from sentry.testutils import APITestCase
from sentry.snuba.models import QueryDatasets


class IncidentListEndpointTest(APITestCase):
    endpoint = "sentry-api-0-organization-incident-index"

    @fixture
    def organization(self):
        return self.create_organization()

    @fixture
    def project(self):
        return self.create_project(organization=self.organization)

    @fixture
    def user(self):
        return self.create_user()

    def test_simple(self):
        self.create_team(organization=self.organization, members=[self.user])
        incident = self.create_incident()
        other_incident = self.create_incident(status=IncidentStatus.CLOSED.value)

        self.login_as(self.user)
        with self.feature(["organizations:incidents", "organizations:performance-view"]):
            resp = self.get_valid_response(self.organization.slug)

        assert resp.data == serialize([other_incident, incident])

    def test_filter_status(self):
        self.create_team(organization=self.organization, members=[self.user])
        incident = self.create_incident()
        closed_incident = self.create_incident(status=IncidentStatus.CLOSED.value)
        self.login_as(self.user)

        with self.feature(["organizations:incidents", "organizations:performance-view"]):
            resp_closed = self.get_valid_response(self.organization.slug, status="closed")
            resp_open = self.get_valid_response(self.organization.slug, status="open")

        assert len(resp_closed.data) == 1
        assert len(resp_open.data) == 1
        assert resp_closed.data == serialize([closed_incident])
        assert resp_open.data == serialize([incident])

    def test_filter_env(self):
        self.create_team(organization=self.organization, members=[self.user])
        env = self.create_environment(self.project)
        rule = self.create_alert_rule(projects=[self.project], environment=env)

        incident = self.create_incident(alert_rule=rule)
        self.create_incident()

        self.login_as(self.user)

        with self.feature(["organizations:incidents", "organizations:performance-view"]):
            resp_filter_env = self.get_valid_response(self.organization.slug, environment=env.name)
            resp_no_env_filter = self.get_valid_response(self.organization.slug)

        # The alert without an environment assigned should not be selected
        assert len(resp_filter_env.data) == 1
        assert resp_filter_env.data == serialize([incident])

        # No filter returns both incidents
        assert len(resp_no_env_filter.data) == 2

    def test_no_feature(self):
        self.create_team(organization=self.organization, members=[self.user])
        self.login_as(self.user)
        resp = self.get_response(self.organization.slug)
        assert resp.status_code == 404

    def test_no_perf_alerts(self):
        self.create_team(organization=self.organization, members=[self.user])
        # alert_rule = self.create_alert_rule()
        perf_alert_rule = self.create_alert_rule(query="p95", dataset=QueryDatasets.TRANSACTIONS)

        perf_incident = self.create_incident(alert_rule=perf_alert_rule)
        incident = self.create_incident()

        self.login_as(self.user)
        with self.feature("organizations:incidents"):
            resp = self.get_valid_response(self.organization.slug)
            assert resp.data == serialize([incident])

        with self.feature(["organizations:incidents", "organizations:performance-view"]):
            resp = self.get_valid_response(self.organization.slug)
            assert resp.data == serialize([incident, perf_incident])

    def test_filter_start_end_times(self):
        self.create_team(organization=self.organization, members=[self.user])
        old_incident = self.create_incident(date_started=timezone.now() - timedelta(hours=26))
        update_incident_status(
            incident=old_incident,
            status=IncidentStatus.CLOSED,
            date_closed=timezone.now() - timedelta(hours=25),
        )
        new_incident = self.create_incident(date_started=timezone.now() - timedelta(hours=2))
        update_incident_status(
            incident=new_incident,
            status=IncidentStatus.CLOSED,
            date_closed=timezone.now() - timedelta(hours=1),
        )
        self.login_as(self.user)
        with self.feature(["organizations:incidents", "organizations:performance-view"]):
            resp_all = self.get_valid_response(self.organization.slug)
            resp_new = self.get_valid_response(
                self.organization.slug,
                start=(timezone.now() - timedelta(hours=12)).isoformat(),
                end=timezone.now().isoformat(),
            )
            resp_old = self.get_valid_response(
                self.organization.slug,
                start=(timezone.now() - timedelta(hours=36)).isoformat(),
                end=(timezone.now() - timedelta(hours=24)).isoformat(),
            )

        assert resp_all.data == serialize([new_incident, old_incident])
        assert resp_new.data == serialize([new_incident])
        assert resp_old.data == serialize([old_incident])
