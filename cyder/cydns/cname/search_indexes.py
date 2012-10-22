from haystack import indexes
from cyder.cydns.cname.models import CNAME
from cyder.cydns.cydns_index import MozdnsIndex


class CNAMEIndex(MozdnsIndex, indexes.Indexable):
    data = indexes.CharField(model_attr='data')

    def get_model(self):
        return CNAME
