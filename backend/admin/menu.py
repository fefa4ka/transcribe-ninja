from wpadmin.menu.menus import Menu
from wpadmin.menu import items


class TopMenu(Menu):
    """
    My super new menu ;)
    """

    def init_with_context(self, context):
        self.children += [
            items.ModelList(
                title='Humanity',
                icon='fa-money',
                models=('django.contrib.auth.*', 'work.payment.Payment',),
            ),
            items.ModelList(
                title='Process',
                icon='fa-tasks',
                models=('transcribe.record.Record', 'work.queue.Queue'),
            ),

        ]
