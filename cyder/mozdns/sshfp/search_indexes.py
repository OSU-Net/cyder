from haystack import indexes
from cyder.mozdns.txt.models import TXT
from cyder.mozdns.mozdns_index import MozdnsIndex


class TXTIndex(MozdnsIndex, indexes.Indexable):
    txt_data = indexes.CharField(model_attr='txt_data')

    def get_model(self):
        return TXT
