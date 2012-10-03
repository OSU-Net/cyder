from haystack import indexes
from cyder.mozdns.address_record.models import AddressRecord
from cyder.mozdns.mozdns_index import MozdnsIndex


class AddressRecordIndex(MozdnsIndex, indexes.Indexable):
    ip_str = indexes.CharField(model_attr='ip_str')

    def get_model(self):
        return AddressRecord
