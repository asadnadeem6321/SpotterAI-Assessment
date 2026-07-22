from rest_framework import serializers


class TripPlanRequestSerializer(serializers.Serializer):
    current_location = serializers.CharField(required=True, trim_whitespace=True)
    pickup_location = serializers.CharField(required=True, trim_whitespace=True)
    dropoff_location = serializers.CharField(required=True, trim_whitespace=True)
    current_cycle_used_hours = serializers.FloatField(required=True, min_value=0, max_value=70)
