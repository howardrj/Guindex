import logging

from rest_framework import generics
from rest_framework import permissions

from GuindexUser.models import GuindexUser
from GuindexUser.serializers import GuindexUserSerializer

logger = logging.getLogger(__name__)


class ContributionsList(generics.ListAPIView):

    serializer_class   = GuindexUserSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.error("Received ContributionsList request")

        # Access base class constructor
        super(ContributionsList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return GuindexUser.objects.all()


class ContributionsDetail(generics.RetrieveAPIView):

    serializer_class   = GuindexUserSerializer
    permission_classes = (permissions.AllowAny, )

    def __init__(self, *args, **kwargs):

        logger.error("Received ContributionsDetail request")

        # Access base class constructor
        super(ContributionsDetail, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return GuindexUser.objects.all()
