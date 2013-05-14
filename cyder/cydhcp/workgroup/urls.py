from cyder.cydhcp.urls import cydhcp_urls

urlpatterns = cydhcp_urls('workgroup') + cydhcp_urls('workgroup_kv')
