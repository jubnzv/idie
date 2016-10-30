from django.conf import settings
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',
        views.IndexView.as_view(
            board_id=settings.NEWS_BOARD_ID,
        ),
        name='news-page'),
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
