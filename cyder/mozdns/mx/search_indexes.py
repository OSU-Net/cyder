from haystack import indexes
from cyder.mozdns.mx.models import MX
from cyder.mozdns.mozdns_index import MozdnsIndex


class MXIndex(MozdnsIndex, indexes.Indexable):
    server = indexes.CharField(model_attr='server')

    def get_model(self):
        return MX
