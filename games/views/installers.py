from __future__ import absolute_import

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from reversion.models import Version

from common.permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAdminUser
from games import models, serializers


class InstallerListView(generics.ListAPIView):
    serializer_class = serializers.InstallerSerializer
    queryset = models.Installer.objects.all()


class InstallerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.InstallerSerializer
    queryset = models.Installer.objects.all()


class GameRevisionListView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = serializers.GameRevisionSerializer
    queryset = models.Game.objects.all()
    lookup_field = 'slug'


class GameInstallerList(generics.ListAPIView):
    serializer_class = serializers.InstallerSerializer

    def get_queryset(self):
        game_slug = self.request.parser_context['kwargs']['slug']
        return models.Installer.objects.filter(game__slug=game_slug)


class InstallerRevisionListView(generics.ListAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.InstallerRevisionSerializer

    def get_queryset(self):
        installer = models.Installer.objects.get(pk=self.request.parser_context['kwargs']['pk'])
        return installer.revisions


class InstallerRevisionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.InstallerRevisionSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.data.get('action') == 'accept':
            instance.accept()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def get_object(self):
        version = Version.objects.get(pk=self.request.parser_context['kwargs']['pk'])
        return models.InstallerRevision(version)
