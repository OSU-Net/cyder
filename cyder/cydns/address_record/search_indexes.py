from haystack import indexes
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cydns_index import CydnsIndex


class AddressRecordIndex(CydnsIndex, indexes.Indexable):
    ip_str = indexes.CharField(model_attr='ip_str')

    def get_model(self):
        return AddressRecord
