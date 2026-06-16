from rest_framework import serializers
from .models import SyncQueue, OperationType

class SyncOperationInputSerializer(serializers.Serializer):
    client_operation_id = serializers.UUIDField()
    operation_type = serializers.ChoiceField(choices=OperationType.choices)
    model_name = serializers.CharField(max_length=100)
    payload = serializers.JSONField()

class SyncBatchInputSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    operations = SyncOperationInputSerializer(many=True, max_length=50)

class SyncReportItemSerializer(serializers.Serializer):
    client_operation_id = serializers.UUIDField()
    status = serializers.CharField()
    message = serializers.CharField(required=False, allow_null=True)

class SyncBatchResponseSerializer(serializers.Serializer):
    processed = serializers.IntegerField()
    conflicts = serializers.IntegerField()
    errors = serializers.IntegerField()
    details = SyncReportItemSerializer(many=True)
    server_time = serializers.DateTimeField(read_only=True)