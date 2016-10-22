from django import template
from board.models import Board

register = template.Library()


@register.inclusion_tag('board/navigation.html')
def get_board_list(boards):
    return {'boards': Board.objects.all()}
