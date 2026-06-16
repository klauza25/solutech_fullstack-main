from django.urls import path
from .views import SyncPushView,SyncStatusView, SyncPingView, SyncDeltaView

urlpatterns = [
    path("push/", SyncPushView.as_view(), name="sync_push"),
    path("status/", SyncStatusView.as_view(), name="sync_status"),  # Phase 3
    path("ping/", SyncPingView.as_view(), name="sync_ping"),
    path("delta/", SyncDeltaView.as_view(), name="sync_delta"),
    
]