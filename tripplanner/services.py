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
    warnings: List[str]
    cycle_status: str


class TripPlanningService:
    MAX_CYCLE_HOURS = 70
    MAX_DAILY_DRIVE_HOURS = 11
    MAX_DAILY_ON_DUTY_HOURS = 14
    REFUEL_INTERVAL_MILES = 1000
    PICKUP_DROPOFF_BUFFER_HOURS = 1
    AVERAGE_SPEED_MPH = 55
    REQUIRED_REST_HOURS = 10 / 60
    REQUIRED_OFF_DUTY_HOURS = 8 / 60

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
        day_number = 1
        while remaining_drive > 0:
            day_drive_hours = min(remaining_drive, self.MAX_DAILY_DRIVE_HOURS)
            day_on_duty_hours = min(day_drive_hours + self.PICKUP_DROPOFF_BUFFER_HOURS, self.MAX_DAILY_ON_DUTY_HOURS)
            daily_entry = {
                'day': day_number,
                'drive_hours': round(day_drive_hours, 2),
                'on_duty_hours': round(day_on_duty_hours, 2),
                'rest_required': day_drive_hours >= self.MAX_DAILY_DRIVE_HOURS,
                'cycle_hours_used': round(min(current_cycle_used + day_drive_hours, self.MAX_CYCLE_HOURS), 2),
            }
            daily_logs.append(daily_entry)
            eld_logs.append({
                'day': day_number,
                'driving_hours': round(day_drive_hours, 2),
                'on_duty_hours': round(day_on_duty_hours, 2),
                'off_duty_hours': round(max(0, 24 - day_on_duty_hours), 2),
                'status': 'Rest Required' if day_drive_hours >= self.MAX_DAILY_DRIVE_HOURS else 'Driving',
                'remarks': 'Fueling stop recommended' if day_number > 1 else 'Ready for dispatch',
            })
            remaining_drive -= day_drive_hours
            day_number += 1

        cycle_status = 'within-cycle'
        if remaining_cycle <= 0:
            cycle_status = 'exceeded'
        elif current_cycle_used + drive_hours > self.MAX_CYCLE_HOURS * 0.85:
            cycle_status = 'near-limit'

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
