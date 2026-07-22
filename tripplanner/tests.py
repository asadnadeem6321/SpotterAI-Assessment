from django.test import SimpleTestCase
from rest_framework.test import APIClient

from .services import TripPlanningService


class TripPlanningServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = TripPlanningService()

    def test_build_trip_plan_returns_expected_structure(self):
        payload = {
            'current_location': 'Chicago',
            'pickup_location': 'Detroit',
            'dropoff_location': 'Cleveland',
            'current_cycle_used_hours': 20,
        }

        plan = self.service.build_trip_plan(payload)

        self.assertEqual(plan.current_location, 'Chicago')
        self.assertGreater(plan.total_distance_miles, 0)
        self.assertGreater(plan.total_drive_hours, 0)
        self.assertEqual(len(plan.daily_logs), 1)
        self.assertIn(plan.cycle_status, {'within-cycle', 'near-limit', 'exceeded'})

    def test_build_trip_plan_marks_multiple_days_for_longer_journeys(self):
        payload = {
            'current_location': 'Chicago',
            'pickup_location': 'Denver',
            'dropoff_location': 'Phoenix',
            'current_cycle_used_hours': 5,
        }

        plan = self.service.build_trip_plan(payload)

        self.assertGreaterEqual(len(plan.daily_logs), 2)

    def test_build_trip_plan_includes_eld_log_entries(self):
        payload = {
            'current_location': 'Chicago',
            'pickup_location': 'Detroit',
            'dropoff_location': 'Cleveland',
            'current_cycle_used_hours': 20,
        }

        plan = self.service.build_trip_plan(payload)

        self.assertEqual(len(plan.eld_logs), len(plan.daily_logs))
        self.assertIn('driving_hours', plan.eld_logs[0])
        self.assertIn('status', plan.eld_logs[0])

    def test_api_returns_validation_error_for_missing_fields(self):
        client = APIClient()
        response = client.post('/api/trip-plan/', {}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('current_location', response.json())
