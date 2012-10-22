from haystack import indexes
from cyder.cydns.txt.models import TXT
from cyder.cydns.cydns_index import MozdnsIndex


class TXTIndex(MozdnsIndex, indexes.Indexable):
    txt_data = indexes.CharField(model_attr='txt_data')

    def get_model(self):
        return TXT
