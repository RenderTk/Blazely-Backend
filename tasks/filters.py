import django_filters
from .models import Task, TaskStep

class TaskFilter(django_filters.FilterSet):
    has_reminder = django_filters.BooleanFilter(
        field_name="reminder_date",
        lookup_expr="isnull",
        label="Has reminder",
        exclude=True,
    )
    has_due_date = django_filters.BooleanFilter(
        field_name="due_date", lookup_expr="isnull", label="Has due date", exclude=True
    )

    class Meta:
        model = Task
        fields = {
            "text": ["icontains"],
            "note": ["icontains"],
            "is_completed": ["exact"],
            "is_important": ["exact"],
            "due_date": ["gt", "lte", "exact"],
            "task_list": ["exact"],
            "priority": ["exact"],
            "label": ["exact"],
        }

class TaskStepFilter(django_filters.FilterSet):
    class Meta:
        model = TaskStep
        fields = {
            "task": ["exact"],
            "text": ["icontains"],
        }