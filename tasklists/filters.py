from django_filters import rest_framework as django_filters
from .models import TaskList

class TaskListFilter(django_filters.FilterSet):

    has_group = django_filters.BooleanFilter(
        field_name="group", lookup_expr="isnull", label="Has Group", exclude=True
    )

    class Meta:
        model = TaskList
        fields = {
            "name": ["icontains"],
            "group": ["exact"],
        }