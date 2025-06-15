from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import GroupList
from .serializers import GroupListSerializer, ManageListsOnGroupSerializer
from .filters import GroupListFilter


class GroupListViewSet(ModelViewSet):
    serializer_class = GroupListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = GroupListFilter

    def get_queryset(self):
        user = self.request.user

        return (
            GroupList.objects.prefetch_related("lists__tasks__steps")
            .filter(owner__user=user)
            .order_by("created_at")
        )

    def get_serializer_class(self):
        if self.action == "manage_lists":
            return ManageListsOnGroupSerializer
        return GroupListSerializer

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}

    @action(detail=True, methods=["patch"])
    def manage_lists(self, request, pk=None):
        action = self.request.query_params.get("action", None)
        if action not in ["add", "remove"]:
            return Response(
                {"action": "Invalid or missing action. Expected 'add' or 'remove'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # gets the group object in the url and validates if it exists
        # and if the user is the owner
        group_list: GroupList = self.get_object()

        serializer = ManageListsOnGroupSerializer(
            data=request.data, context={"group_list": group_list, "action": action}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": f"Lists successfully {'added' if action == 'add' else 'removed'}"
            },
            status=status.HTTP_200_OK,
        )