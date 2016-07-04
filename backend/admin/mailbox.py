#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin

from django_mailbox.admin import *

from dbmail.models import MailTemplate

from site import admin_site


class MailTemplateAdmin(ModelAdmin):
    pass


admin_site.register(Message, MessageAdmin)
admin_site.register(MessageAttachment, MessageAttachmentAdmin)
admin_site.register(Mailbox, MailboxAdmin)

admin_site.register(MailTemplate, MailTemplateAdmin)
