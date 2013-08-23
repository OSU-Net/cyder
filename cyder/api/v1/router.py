from rest_framework.routers import Route, SimpleRouter

class CyderRouter(SimpleRouter):
    """Custom routing to add key-value support."""
    routes = [
        Route(url=r'^{prefix}$',
              mapping={'get': 'list'},
              name='{basename}-list',
              initkwargs={'suffix': 'List'}),
        Route(url=r'^{prefix}/keyvalues$',
              mapping={'get': 'list'},
              name='{basename}-keyvalues-list',
              initkwargs={'suffix': 'List'}),
        Route(url=r'^{prefix}/{lookup}$',
              mapping={'get': 'retrieve'},
              name='{basename}-detail',
              initkwargs={'suffix': 'Detail'}),
        Route(url=r'^{prefix}/keyvalues/{lookup}$',
              mapping={'get': 'retrieve'},
              name='{basename}-keyvalues-detail',
              initkwargs={'suffix': 'Detail'}),
    ]
