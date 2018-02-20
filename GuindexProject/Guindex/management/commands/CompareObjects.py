import logging
from itertools import chain

from django.core.management.base import BaseCommand

from Guindex.GuindexBot import GuindexBot
from Guindex.models import Pub

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        pub1 = Pub.objects.get(id = 62)
        pub2 = Pub.objects.get(id = 63)

        field_names = list(set(chain.from_iterable(
            (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
            for field in Pub._meta.get_fields()
            # For complete backwards compatibility, you may want to exclude
            # GenericForeignKey from the results.
            if not (field.many_to_one and field.related_model is None)
        )))


        diffs = filter(lambda field: getattr(pub1, field, None) != getattr(pub2, field, None), field_names)

        print(diffs)
