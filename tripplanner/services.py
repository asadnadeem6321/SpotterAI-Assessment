from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class RestBreak:
    label: str
    duration_hours: float
    reason: str


@dataclass
class TripPlan:
    current_location: str
    pickup_location: str
    dropoff_location: str
    current_cycle_used_hours: float
    total_distance_miles: float
    total_drive_hours: float
    total_on_duty_hours: float
    remaining_cycle_hours: float
    required_rest_breaks: List[RestBreak]
    daily_logs: List[dict]
    eld_logs: List[dict]
    route_summary: List[dict]
    route_map: dict
    warnings: List[str]
    cycle_status: str


class TripPlanningService:
    MAX_CYCLE_HOURS = 70
    CYCLE_WINDOW_DAYS = 8
    MAX_DAILY_DRIVE_HOURS = 11
    MAX_DAILY_ON_DUTY_HOURS = 14
    REFUEL_INTERVAL_MILES = 1000
    PICKUP_DROPOFF_BUFFER_HOURS = 1
    AVERAGE_SPEED_MPH = 55
    REQUIRED_REST_HOURS = 10 / 60
    REQUIRED_OFF_DUTY_HOURS = 8 / 60
    CITY_COORDINATES = {
        'chicago': {'lat': 41.8781, 'lng': -87.6298},
        'detroit': {'lat': 42.3314, 'lng': -83.0458},
        'cleveland': {'lat': 41.4993, 'lng': -81.6944},
        'denver': {'lat': 39.7392, 'lng': -104.9903},
        'phoenix': {'lat': 33.4484, 'lng': -112.0740},
        'lasvegas': {'lat': 36.1699, 'lng': -115.1398},
    }

    def build_trip_plan(self, data: dict) -> TripPlan:
        current_cycle_used = float(data['current_cycle_used_hours'])
        total_distance = self._estimate_distance_miles(data['current_location'], data['pickup_location'], data['dropoff_location'])
        drive_hours = total_distance / self.AVERAGE_SPEED_MPH
        on_duty_hours = drive_hours + self.PICKUP_DROPOFF_BUFFER_HOURS
        remaining_cycle = self.MAX_CYCLE_HOURS - current_cycle_used

        rest_breaks = []
        warnings = []

        if current_cycle_used >= self.MAX_CYCLE_HOURS:
            warnings.append('Current cycle already exceeds the maximum allowed hours.')
        if current_cycle_used + drive_hours > self.MAX_CYCLE_HOURS:
            warnings.append('This trip would exceed the remaining cycle hours.')

        if drive_hours > self.MAX_DAILY_DRIVE_HOURS:
            rest_breaks.append(RestBreak('Required rest', self.REQUIRED_REST_HOURS, 'Daily driving limit exceeded'))
        if on_duty_hours > self.MAX_DAILY_ON_DUTY_HOURS:
            rest_breaks.append(RestBreak('Extended duty break', self.REQUIRED_OFF_DUTY_HOURS, 'Daily on-duty limit exceeded'))

        refuel_count = max(1, int(total_distance // self.REFUEL_INTERVAL_MILES))
        if refuel_count > 1:
            rest_breaks.append(RestBreak('Fuel stop', 0.25, f'Fueling required at least {refuel_count} times'))

        daily_logs = []
        eld_logs = []
        remaining_drive = drive_hours
        remaining_cycle_after_day = current_cycle_used
        day_number = 1
        while remaining_drive > 0:
            day_drive_hours = min(remaining_drive, self.MAX_DAILY_DRIVE_HOURS)
            day_on_duty_hours = min(day_drive_hours + self.PICKUP_DROPOFF_BUFFER_HOURS, self.MAX_DAILY_ON_DUTY_HOURS)
            remaining_cycle_after_day = min(self.MAX_CYCLE_HOURS, remaining_cycle_after_day + day_drive_hours)
            daily_entry = {
                'day': day_number,
                'drive_hours': round(day_drive_hours, 2),
                'on_duty_hours': round(day_on_duty_hours, 2),
                'rest_required': day_drive_hours >= self.MAX_DAILY_DRIVE_HOURS,
                'cycle_hours_used': round(remaining_cycle_after_day, 2),
                'cycle_window_days': self.CYCLE_WINDOW_DAYS,
                'rolling_cycle_days_remaining': max(0, self.CYCLE_WINDOW_DAYS - day_number),
            }
            daily_logs.append(daily_entry)
            eld_logs.append({
                'day': day_number,
                'driving_hours': round(day_drive_hours, 2),
                'on_duty_hours': round(day_on_duty_hours, 2),
                'off_duty_hours': round(max(0, 24 - day_on_duty_hours), 2),
                'status': 'Rest Required' if day_drive_hours >= self.MAX_DAILY_DRIVE_HOURS else 'Driving',
                'remarks': 'Fueling stop recommended' if day_number > 1 else 'Ready for dispatch',
                'cycle_window_days': self.CYCLE_WINDOW_DAYS,
            })
            remaining_drive -= day_drive_hours
            day_number += 1

        cycle_status = 'within-cycle'
        if remaining_cycle <= 0:
            cycle_status = 'exceeded'
        elif current_cycle_used + drive_hours > self.MAX_CYCLE_HOURS * 0.85:
            cycle_status = 'near-limit'

        route_summary = [
            {
                'step': 1,
                'location': data['current_location'],
                'type': 'Start',
                'instruction': 'Depart from the current location and prepare for pickup.',
                'distance_miles': round(total_distance * 0.2, 2),
                'estimated_duration_hours': round(drive_hours * 0.2, 2),
            },
            {
                'step': 2,
                'location': data['pickup_location'],
                'type': 'Pickup',
                'instruction': 'Complete the pickup handoff and verify the load before continuing.',
                'distance_miles': round(total_distance * 0.4, 2),
                'estimated_duration_hours': round(drive_hours * 0.4, 2),
            },
            {
                'step': 3,
                'location': data['dropoff_location'],
                'type': 'Dropoff',
                'instruction': 'Deliver the shipment and finalize the route.',
                'distance_miles': round(total_distance * 0.4, 2),
                'estimated_duration_hours': round(drive_hours * 0.4, 2),
            },
        ]

        route_map = {
            'center': self._get_coordinates(data['pickup_location']),
            'points': [
                {
                    'label': 'Start',
                    'location': data['current_location'],
                    **self._get_coordinates(data['current_location']),
                },
                {
                    'label': 'Pickup',
                    'location': data['pickup_location'],
                    **self._get_coordinates(data['pickup_location']),
                },
                {
                    'label': 'Dropoff',
                    'location': data['dropoff_location'],
                    **self._get_coordinates(data['dropoff_location']),
                },
            ],
            'path': [
                self._get_coordinates(data['current_location']),
                self._get_coordinates(data['pickup_location']),
                self._get_coordinates(data['dropoff_location']),
            ],
        }

        return TripPlan(
            current_location=data['current_location'],
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location'],
            current_cycle_used_hours=current_cycle_used,
            total_distance_miles=round(total_distance, 2),
            total_drive_hours=round(drive_hours, 2),
            total_on_duty_hours=round(on_duty_hours, 2),
            remaining_cycle_hours=round(remaining_cycle, 2),
            required_rest_breaks=rest_breaks,
            daily_logs=daily_logs,
            eld_logs=eld_logs,
            route_summary=route_summary,
            route_map=route_map,
            warnings=warnings,
            cycle_status=cycle_status,
        )

    def _estimate_distance_miles(self, current_location: str, pickup_location: str, dropoff_location: str) -> float:
        city_map = {
            'chicago': {'detroit': 280, 'cleveland': 345, 'denver': 1000, 'phoenix': 1500},
            'detroit': {'chicago': 280, 'cleveland': 170, 'denver': 1100, 'phoenix': 1600},
            'cleveland': {'chicago': 345, 'detroit': 170, 'denver': 1200, 'phoenix': 1550},
            'denver': {'chicago': 1000, 'phoenix': 600, 'lasvegas': 450},
            'phoenix': {'denver': 600, 'lasvegas': 300, 'chicago': 1500},
            'lasvegas': {'phoenix': 300, 'denver': 450},
        }

        total_distance = 0.0
        segments = [
            (current_location, pickup_location),
            (pickup_location, dropoff_location),
        ]

        for origin, destination in segments:
            origin_key = origin.lower()
            destination_key = destination.lower()
            if origin_key in city_map and destination_key in city_map[origin_key]:
                total_distance += city_map[origin_key][destination_key]
            else:
                total_distance += 350.0

        return round(total_distance, 2)

    def _get_coordinates(self, location: str) -> dict:
        coordinates = self.CITY_COORDINATES.get(location.lower())
        if coordinates:
            return coordinates

        fallback = sum(ord(char) for char in location.lower())
        lat = 30 + (fallback % 1200) / 100
        lng = -120 + (fallback % 1500) / 100
        return {'lat': round(lat, 4), 'lng': round(lng, 4)}
