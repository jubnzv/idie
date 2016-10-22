from django import forms
import datetime

from board.models import Post


class PostForm(forms.ModelForm):
    topic = forms.CharField(
        label="Topic",
    )
    text = forms.CharField(
        label="Post",
        widget=forms.Textarea,
        required=True,
    )
    pub_date = datetime.datetime.now()
    is_op_post = False
    file = None

    def do_post(thread_):
        print("posted.")

    class Meta:
        model = Post
        fields = ["topic", "text"]


# class ThreadForm(forms.ModelForm):
#     """Uses in thread creation routine. Not implemented yet.

#     It will content thread-specific fields like:
#     * moderator password
#     * tags
#     * user-specified slug
#     * etc.
#     """
#     class Meta:
#         model = Thread
