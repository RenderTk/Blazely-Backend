import django_filters 
from .models import GroupList

class GroupListFilter(django_filters.FilterSet):
    class Meta:
        model = GroupList
        fields = {
            "name": ["icontains"],
        }
