from haystack import indexes
from cyder.cydns.mx.models import MX
from cyder.cydns.cydns_index import MozdnsIndex


class MXIndex(MozdnsIndex, indexes.Indexable):
    server = indexes.CharField(model_attr='server')

    def get_model(self):
        return MX
