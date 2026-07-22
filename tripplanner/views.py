from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TripPlanRequestSerializer
from .services import TripPlanningService


service = TripPlanningService()


def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'tripplanner-api',
        'message': 'Django backend is running successfully.'
    })


@api_view(['POST'])
def create_trip_plan(request):
    serializer = TripPlanRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    plan = service.build_trip_plan(serializer.validated_data)
    return Response({
        'current_location': plan.current_location,
        'pickup_location': plan.pickup_location,
        'dropoff_location': plan.dropoff_location,
        'current_cycle_used_hours': plan.current_cycle_used_hours,
        'total_distance_miles': plan.total_distance_miles,
        'total_drive_hours': plan.total_drive_hours,
        'total_on_duty_hours': plan.total_on_duty_hours,
        'remaining_cycle_hours': plan.remaining_cycle_hours,
        'required_rest_breaks': [
            {
                'label': break_item.label,
                'duration_hours': break_item.duration_hours,
                'reason': break_item.reason,
            }
            for break_item in plan.required_rest_breaks
        ],
        'daily_logs': plan.daily_logs,
        'eld_logs': plan.eld_logs,
        'warnings': plan.warnings,
        'cycle_status': plan.cycle_status,
    }, status=status.HTTP_200_OK)
