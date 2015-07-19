from wpadmin.menu.menus import Menu
from wpadmin.menu import items


class TopMenu(Menu):
    """
    My super new menu ;)
    """

    def init_with_context(self, context):
        self.children += [
            items.AppList(
                title='Records',
                icon='fa-tasks',
                models=('transcribe.record.Record',),
            ),
            items.ModelList(
                title='Payments',
                icon='fa-money',
                models=('work.payment.*',),
            ),

        ]
