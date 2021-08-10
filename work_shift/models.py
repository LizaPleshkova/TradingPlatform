from django.db import models


class Plan(models.Model):
    name = models.CharField("Plan", max_length=255, null=True, blank=True)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return f'{self.id} - {self.name} - {self.start} - {self.end}'


class WorkShift(models.Model):
    name = models.CharField("Work shift", max_length=255, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    plan = models.ForeignKey(Plan, blank=True, null=True, on_delete=models.SET_NULL, related_name='workshift_plan')

    def __str__(self):
        return f'{self.id} - {self.name} - {self.start_date} - {self.end_date}- {self.plan.name}'


class Position(models.Model):
    first_name = models.CharField("First name", max_length=255, null=True, blank=True)
    last_name = models.CharField("Last name", max_length=255, null=True, blank=True)
    email = models.CharField("Email", max_length=255, null=True, blank=True)
    workshifts = models.ManyToManyField(WorkShift, blank=True, related_name='assigned_positions')


    def __str__(self):
        return f'{self.id} - {self.first_name} - {self.last_name} - {self.email}'
