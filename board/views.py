from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.conf import settings

import datetime

from .models import Board, Thread, Post
from .forms import PostForm


class BoardView(ListView):
    """
    Representation of board: contents list of threads.
    """
    template_name = 'board/board.djhtml'
    paginate_by = settings.THREADS_ON_PAGE
    model = Thread
    context_object_name = 'thread_list'
    ordering = '-bump_date'
    board_id = None

    def get_queryset(self):
        if self.board_id:
            self.board = get_object_or_404(Board, id=self.board_id)
        else:
            self.board = get_object_or_404(Board, slug=self.kwargs['board_slug'])

        return Thread.objects.filter(board=self.board).order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)
        context['board'] = self.board
        return context


class IndexView(BoardView):
    """
    'Latest news' board representation.
    """
    template_name = 'board/news.djhtml'
    paginate_by = settings.NEWS_ON_PAGE
    conetext_object_name = 'news_list'


class ThreadView(CreateView, SuccessMessageMixin):
    """ Manages list of posts for current thread and reply form."""
    template_name = 'board/thread.djhtml'
    success_message = "Post successfully created!"
    form_class = PostForm
    ordering = 'slug'
    context_object_name = 'post_list'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        self.object = None
        return super(ThreadView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """Returns post list for current thread."""
        thread = get_object_or_404(Thread, slug=self.kwargs['thread_slug'])
        return Post.objects.filter(thread=thread).order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super(ThreadView, self).get_context_data(**kwargs)

        # TODO: ugly~
        context['post_list'] = self.get_queryset()
        context['board'] = Board.objects.get(slug=self.kwargs['board_slug'])

        return context

    def form_valid(self, form, **kwargs):
        # TODO: get values from context - ?
        post = form.instance

        board_slug = self.kwargs['board_slug']
        board = Board.objects.get(slug=board_slug)
        thread_slug = self.kwargs['thread_slug']
        thread = Thread.objects.get(slug=thread_slug, board=board)

        post.pub_date = datetime.datetime.now()
        post.thread_id = thread.id

        # Update bump date for thread
        if post.is_sage is False:
            thread.bump_date = post.pub_date
            thread.save()

        form.instance = post

        return super(ThreadView, self).form_valid(form)


class CreateThreadView(SuccessMessageMixin, CreateView):
    """ Create thread form (separate page) """
    template_name = 'board/board_create_thread.djhtml'
    form_class = PostForm
    success_message = "Thread was successfully created!"

    def get_context_data(self, **kwargs):
        context = super(CreateThreadView, self).get_context_data(**kwargs)
        context['board'] = Board.objects.get(slug=self.kwargs['board_slug'])

        return context

    def form_valid(self, form, **kwargs):
        time_now = datetime.datetime.now()

        board_slug = self.kwargs['board_slug']
        board = Board.objects.get(slug=board_slug)

        thread = Thread()
        thread.id = board.next_thread_num()
        thread.board = board
        thread.bump_date = time_now
        thread.save()

        post = form.instance
        post.pub_date = time_now
        post.is_op_post = True
        post.is_sage = False
        post.thread = thread

        form.instance = post
        return super(CreateThreadView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('board-page',
                            kwargs={'board_slug': self.kwargs['board_slug']})
