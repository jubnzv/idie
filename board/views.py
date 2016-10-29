from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

import datetime

from .models import Board, Thread, Post
from .forms import PostForm


class IndexView(TemplateView):
    """ List of boards + latest news."""
    template_name = 'board/index.html'

    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super(IndexView, self).get_context_data(**kwargs)

        context['boards_list'] = Board.objects.all()

        # TODO: Hardcoded news board id
        news_board = Board.objects.get(id=1)
        context['news_list'] = Thread.objects.filter(board=news_board)

        return context


class BoardView(ListView):
    """ List of threads for selected board """
    template_name = 'board/board.html'
    # TODO: Hardcoded paginate_by number. Use config.ini here later~ 
    paginate_by = 5
    model = Thread
    context_object_name = 'thread_list'
    ordering = '-bump_date'

    def get_queryset(self):
        self.board = get_object_or_404(Board, slug=self.kwargs['board_slug'])
        return Thread.objects.filter(board=self.board).order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)
        context['board'] = self.board
        return context


class ThreadView(CreateView, SuccessMessageMixin):
    """ Manages list of posts for current thread and reply form."""
    template_name = 'board/thread.html'
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
        context['post_list'] = self.get_queryset() # TODO: ugly~
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
    template_name = 'board/create_thread.html'
    form_class = PostForm
    success_message = "Thread was successfully created!"

    def get_context_data(self, **kwargs):
        context = super(CreateThreadView, self).get_context_data(**kwargs)
        this_board = Board.objects.get(slug=self.kwargs['board_slug'])

        context['board_is_ro'] = this_board.is_ro

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
