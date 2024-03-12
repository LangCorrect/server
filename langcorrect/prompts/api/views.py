from rest_framework import generics
from rest_framework import permissions

from config.api.permissions import IsOwnerOrStaff
from langcorrect.prompts.api.serializers import PromptSerializer
from langcorrect.prompts.models import Prompt


class PromptListCreateAPIView(generics.ListCreateAPIView):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related(
            "user",
            "language",
            "challenge",
        ).prefetch_related("tags")

        search = self.request.query_params.get("search")
        langs = self.request.query_params.get("langs")

        if search:
            queryset = queryset.filter(content__icontains=search)

        if langs:
            codes = langs.split(",")
            queryset = queryset.filter(language__code__in=codes)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PromptRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    lookup_field = "slug"
    permission_classes = [IsOwnerOrStaff]

    def get_queryset(self):
        return self.queryset.select_related(
            "user",
            "language",
            "challenge",
        ).prefetch_related("tags")

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            permission_classes = [IsOwnerOrStaff]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        updates = {}
        language = serializer.validated_data.get("lang_code")
        if language:
            updates["language"] = language
        serializer.save(user=self.request.user, **updates)
