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
    warnings: List[str]


class TripPlanningService:
    MAX_CYCLE_HOURS = 70
    MAX_DAILY_DRIVE_HOURS = 11
    MAX_DAILY_ON_DUTY_HOURS = 14
    REFUEL_INTERVAL_MILES = 1000
    PICKUP_DROPOFF_BUFFER_HOURS = 1
    AVERAGE_SPEED_MPH = 55

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

        if drive_hours > self.MAX_DAILY_DRIVE_HOURS:
            rest_breaks.append(RestBreak('Required rest', 10.0 / 60.0, 'Daily driving limit exceeded'))

        if on_duty_hours > self.MAX_DAILY_ON_DUTY_HOURS:
            rest_breaks.append(RestBreak('Extended duty break', 8.0 / 60.0, 'Daily on-duty limit exceeded'))

        refuel_count = max(1, int(total_distance // self.REFUEL_INTERVAL_MILES))
        if refuel_count > 1:
            rest_breaks.append(RestBreak('Fuel stop', 0.25, f'Fueling required at least {refuel_count} times'))

        daily_logs = []
        remaining_drive = drive_hours
        day_number = 1
        while remaining_drive > 0:
            day_drive_hours = min(remaining_drive, self.MAX_DAILY_DRIVE_HOURS)
            daily_logs.append({
                'day': day_number,
                'drive_hours': round(day_drive_hours, 2),
                'on_duty_hours': round(min(day_drive_hours + self.PICKUP_DROPOFF_BUFFER_HOURS, self.MAX_DAILY_ON_DUTY_HOURS), 2),
                'rest_required': day_drive_hours >= self.MAX_DAILY_DRIVE_HOURS,
            })
            remaining_drive -= day_drive_hours
            day_number += 1

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
            warnings=warnings,
        )

    def _estimate_distance_miles(self, current_location: str, pickup_location: str, dropoff_location: str) -> float:
        base_distance = 350.0
        if current_location.lower() == pickup_location.lower():
            base_distance += 20.0
        if pickup_location.lower() == dropoff_location.lower():
            base_distance += 10.0
        return base_distance
