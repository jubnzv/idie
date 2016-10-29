from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',
        views.IndexView.as_view(),
        name='index-page'),
    # url(r'^(?P<board_slug>\w+)/page(?P<page>[0-9]+)/$',
    #     views.BoardView.as_view(),
    #     name='board-page'),
    url(r'^(?P<board_slug>\w+)/$',
        views.BoardView.as_view(),
        name='board-page'),
    url(r'^(?P<board_slug>\w+)/(?P<thread_slug>\d+)$',
        views.ThreadView.as_view(),
        name='thread-page'),
    url(r'^(?P<board_slug>\w+)/create_thread$',
        views.CreateThreadView.as_view(),
        name='create-thread-page'),
]
