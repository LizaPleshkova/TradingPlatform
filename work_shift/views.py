from django.contrib.postgres.aggregates import ArrayAgg
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from work_shift.serializers import WSSerializer

from work_shift.models import WorkShift, Position, Plan


# class WorkShiftView(RetrieveModelMixin, viewsets.GenericViewSet):
#     permission_classes = (IsAuthenticated,)
#
#     serializer_classes_by_action = {
#         'retrieve': WSSerializer,
#     }
#
#     def get_queryset(self, *args, **kwargs):
#         return WorkShift.objects.filter(plan=self.kwargs['plan-id'])
#
#     def get_serializer_class(self):
#         return self.serializer_classes_by_action.get(self.action, WSSerializer)
#

@api_view(['GET'])
def shifts_func(request, id, format=None):
    if request.method == 'GET':
        # ws1 = WorkShift.objects.filter(plan__id=id).order_by('id')

        ws1 = WorkShift.objects.filter(plan__id=id).order_by('id')\
                                .annotate(assigned_pos=ArrayAgg('assigned_positions'))

        serWs = WSSerializer(ws1, many=True)
        return Response(serWs.data, status.HTTP_200_OK)
    else:
        return Response(status.HTTP_400_BAD_REQUEST)
