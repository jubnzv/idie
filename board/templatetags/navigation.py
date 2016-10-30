from django import template
from django.conf import settings
from board.models import Board


register = template.Library()


@register.inclusion_tag('navigation.djhtml')
def get_board_list(boards):
    return {'boards': Board.objects.all().exclude(id=settings.NEWS_BOARD_ID)}


@register.inclusion_tag('navigation.djhtml')
def get_news_board(boards):
    return {'news_board': Board.objects.get(id=settings.NEWS_BOARD_ID)}
