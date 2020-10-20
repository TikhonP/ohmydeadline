from rest_framework import generics
from api.serializer import TipSerializer, DeadlineSerializer, ProfileSerializer
from core.models import Deadline, Tip, Profile
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response


class TipApiView(generics.ListCreateAPIView):
    serializer_class = TipSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Tip.objects.filter(is_active=True)
        user = self.request.user
        if user is not None:
            queryset = queryset.filter(user=user)
        return queryset

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.is_active = False
        snippet.save()

        return Response(status=status.HTTP_202_ACCEPTED)


class DeadlineApiView(generics.ListCreateAPIView):
    serializer_class = DeadlineSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            user_agent=self.request.auth.application.name,
        )

    def get_queryset(self):
        queryset = Deadline.objects.all()
        user = self.request.user
        if user is not None:
            queryset = queryset.filter(user=user)
        return queryset


class ProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user'

    def get_queryset(self):
        queryset = Profile.objects.all()
        user = self.request.user
        if user is not None:
            queryset = queryset.get(user=user)
        return queryset
