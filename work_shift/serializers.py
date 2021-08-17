from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from work_shift.models import WorkShift, Position, Plan


# class WSSerializer(serializers.ModelSerializer):
#     ''' without array_arg'''
#     assigned_positions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#
#     class Meta:
#         model = WorkShift
#         fields = ('id', 'name', 'start_date', 'end_date', 'assigned_positions')


class WSSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkShift
        fields = ('id', 'name', 'start_date', 'end_date', 'assigned_positions')

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     print(type(representation), representation)
    #     for i in representation:
    #         print(type(i), i, representation[i])
    #         if i == 'assigned_positions':
    #             representation['assigned_positions'] = [
    #                 print(type(j), 'j') for j in representation[i]
    #             ]
    #     # representation['assigned_positions'] = [
    #     #     i.assigned_positions.values()
    #     #     for i in representation
    #     # ]
    #     # representation['assigned_positions'] = representation.assigned_positions.values()
    #     return representation