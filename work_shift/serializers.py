from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from work_shift.models import WorkShift, Position, Plan


# class WSSerializer(serializers.ModelSerializer):
#     assigned_positions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#
#     class Meta:
#         model = WorkShift
#         fields = ('id', 'name', 'start_date', 'end_date', 'assigned_positions')
#

class WSSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkShift
        fields = ('id', 'name', 'start_date', 'end_date', 'assigned_positions')
