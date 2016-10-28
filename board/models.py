from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class Board(models.Model):
    slug = models.SlugField("Slug", max_length=3, blank=False, unique=True)
    name = models.CharField("Full name", max_length=20, blank=False)
    desc = models.CharField("Description", max_length=100, blank=True)
    author_name = models.CharField("Default author name", max_length=100,
                                   default="Anonymous")
    bumplimit = models.PositiveSmallIntegerField("Max posts in the thread",
                                                 default=500)
    is_ro = models.BooleanField("Users can't create threads on this board",
                                default=False)

    class Meta:
        verbose_name = "Board"
        ordering = ["slug"]

    def set_slug_by_name(self):
        """ First three characters of board name as a slug."""
        return self.name[:3]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.set_slug_by_name()
        super(Board, self).save(*args, **kwargs)

    def threads(self):
        """List of threads for current board."""
        threads = Thread.objects.filter(board=self.id).order_by("-bump_date")
        if threads:
            return threads
        else:
            return None

    def next_thread_num(self):
        """Next thread number for current board."""
        threads = Thread.objects.filter(board=self.id)
        if threads:
            return threads.count() + 1
        else:
            return 1


class Thread(models.Model):
    board = models.ForeignKey(Board)
    slug = models.SlugField("Slug: thread number on this board", blank=False)
    is_pinned = models.BooleanField("Thread is pinned", blank=False,
                                    default=False)
    is_closed = models.BooleanField("Thread is closed/archived", blank=False,
                                    default=False)
    bump_date = models.DateTimeField("Last post date", blank=False)

    class Meta:
        verbose_name = "Thread"

    def posts(self):
        """List of posts for current thread."""
        return self.post_set.all()

    def op_post(self):
        """OP post of current thread."""
        p = self.posts()
        return p.filter(is_op_post=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            board = self.board
            self.slug = board.next_thread_num()
        super(Thread, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return "board:thread-page", [self.pk]


class Post(models.Model):
    thread = models.ForeignKey(Thread)

    image = models.ImageField(
        "Image",
        upload_to="img/",
        blank=True,
    )
    slug = models.SlugField(
        "Slug: post number",
    )
    topic = models.CharField(
        "Topic",
        max_length=50,
        blank=True,
    )
    text = models.TextField(
        "Full post text",
        max_length=5000,
        blank=False,
    )
    pub_date = models.DateTimeField(
        "Publication date",
        auto_now_add=True,
    )
    is_op_post = models.BooleanField(
        "Post is first in the thread",
        default=False,
    )
    is_sage = models.BooleanField(
        "Don't bump the thread",
        default=False,
    )
    author_name = models.CharField(
        "Author's name",
        default="Anonymous",
        max_length=30,
        blank=True,
    )
    author_email = models.EmailField(
        "Author's email",
        null=True,
    )

    class Meta:
        verbose_name = "Post"

    def next_post_num(self):
        """Next post number for current thread."""
        try:
            thread = Thread.objects.get(id=self.thread_id)
            return Post.objects.filter(thread_id=thread.id).count() + 1
        except ObjectDoesNotExist:
            return 1

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.next_post_num()
        super(Post, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        thread = self.thread
        board = thread.board
        return ('thread-page', [board.slug, thread.slug])
