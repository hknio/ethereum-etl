import collections
import logging
import boto3
from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter
from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter
from blockchainetl.file_utils import get_file_handle, close_silently
from datetime import datetime
import csv
import json

from uuid import uuid4

class S3ItemExporter(CompositeItemExporter):

    def __init__(self, filename_mapping=None, bucket=None, converters=()):
        #self.item_types = item_types
        tmpdir = '/tmp/'
        self.logger = logging.getLogger('S3ItemExporter')
        self.filename_mapping = {
                'block': 'blocks.csv',
                'transaction': 'transactions.csv',
                'log': 'logs.json',
                'token_transfer': 'token_transfers.csv',
                'trace': 'traces.csv',
                'contract': 'contracts.csv',
                'token': 'tokens.csv'
                }
        self.field_mapping = {}
        self.file_mapping = {}
        self.exporter_mapping = {}
        self.counter_mapping = {}
        self.bucket = bucket
        self.converter = CompositeItemConverter(converters)
        self.s3 = boto3.client('s3')


    def upload(self, location, filename,type, block_date, item_id):
            self.s3.upload_file(filename, location, "data/dev/ethereum/{}/block_date={}/{}".format(filename.split('.')[0], block_date, item_id))

    def export_items(self, items):
        for item in items: #self.convert_items(items):
            self.export_item(item)

    def convert_items(self, items):
        for item in items:
            yield self.converter.convert_item(item)

    def group_by_item_type(items):
        result = collections.defaultdict(list)
        for item in items:
            result[item.get('type')].append(item)
        return result


   # def export_item(self, item):
   #     item_type = item.get('type', None)
   #     if item_type is None:
   #         raise ValueError('type key is not found in item {}'.format(repr(item)))
   #     print(item)
   #     self.items[item_type].append(item)
    def extract_date_from_file(self, file):
        with open(file, 'r') as f:
            rows = []
            if file.endswith('csv'):
                reader = csv.DictReader(f, delimiter=",")
                next(reader)
                for row in reader:  # each row is a list
                    rows.append(row.get('item_timestamp'))
            elif file.endswith('json'):
                for i in f:
                    data = json.loads(i)
                    rows.append(data.get('item_timestamp'))

            minimus = min(rows, key=lambda x: datetime.strptime(x.split('T')[0], '%Y-%m-%d')) #.strftime('%Y-%m-%d') )
            return minimus.split('T')[0]


    def close(self):
        for item_type, file in self.file_mapping.items():
            close_silently(file)
            counter = self.counter_mapping[item_type]
            if counter is not None and (counter.increment() - 1) > 0:
                self.logger.info('{} items exported: {}'.format(item_type, counter.increment() - 1))
                #self.upload(self.bucket, self.filename_mapping[item.get('type')], datetime.strptime(item.get('item_timestamp').split('T')[0], '%Y-%m-%d').strftime("%Y-%m-%d"), item.get('item_id') + '.' + self.filename_mapping[item.get('type')].split('.')[1])
                self.upload(self.bucket, file.name, item_type, self.extract_date_from_file(file.name), str(uuid4()) + '_' + file.name) # item.get('item_id') + '.' + self.filename_mapping[item.get('type')].split('.')[1])
                self.logger.info("Uploaded {} to S3".format(item_type))