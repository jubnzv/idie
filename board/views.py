from django.views.generic import TemplateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

import datetime

from .models import Board, Thread, Post
from .forms import PostForm


class IndexView(TemplateView):
    """ List of boards + latest news (not implemented) """
    template_name = 'board/index.html'

    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super(IndexView, self).get_context_data(**kwargs)

        context['boards_list'] = Board.objects.all()

        news_board = Board.objects.get(id=2) # TODO
        context['news_list'] = Thread.objects.filter(board=news_board)

        return context


class BoardView(TemplateView):
    """ List of threads for selected board """
    template_name = 'board/board.html'

    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)
        this_board = Board.objects.get(slug=self.kwargs['board_slug'])

        context['this_board_name'] = this_board.name
        context['this_board_desc'] = this_board.desc

        context['is_ro'] = this_board.is_ro

        threads = Thread.objects.filter(board=this_board)
        context['threads_list'] = threads

        return context


class ThreadView(SuccessMessageMixin, CreateView):
    """ List of posts for selected thread """
    template_name = 'board/thread.html'
    success_message = "Post successfully updated!"
    form_class = PostForm

    def get_queryset(self):
        return Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ThreadView, self).get_context_data(**kwargs)
        this_thread = Thread.objects.filter(slug=self.kwargs['thread_slug'])
        posts = Post.objects.filter(thread=this_thread)

        context['posts_list'] = posts

        return context

    def form_valid(self, form, **kwargs):
        post = form.instance

        board_slug = self.kwargs['board_slug']
        board = Board.objects.get(slug=board_slug)

        thread_slug = self.kwargs['thread_slug']
        thread = Thread.objects.get(slug=thread_slug, board=board)

        post.pub_date = datetime.datetime.now()
        post.thread_id = thread.id

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
        post.thread = thread

        form.instance = post
        return super(CreateThreadView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('board-page',
                            kwargs={'board_slug': self.kwargs['board_slug']})