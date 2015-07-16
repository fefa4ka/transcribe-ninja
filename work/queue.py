#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
import django.db.models.signals as signals
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from core.models import *
from transcribe.models import *
from account import Price
from order import Order
from payment import Payment
from datetime import datetime

import numpy as np

from diff_match_patch import diff_match_patch


class Queue(AudioFile):

    """
        Элемент очереди, для стенографирования.
        Каждый элемент содержит информацию о работе,
        нужной для стенографирования задписи.

        Работа может быть:
        1. Стенографирование
        2. Проверка транскрибции

        Работа связана с каким-то куском записи, если стенографируется.
        И с двумя кусками рядом, если проверяется.

        order       - заказ, с которым связана работа
        piece       - кусок, для которого делается работа

        audio_file  - аудиозапись, связанная с этим куском

        price       - прайс, по которому должна быть сделана работа

        work_type   - тип работы: стенографирование TRANSCRIBE
                      или проверка CHECK

        priority    - булевый приоритет
                      False - не приоритетно
                      True - приоритетно

        locked      - время, когда эту задачу отдали на выполнение

        owner       - кому отдали задачу, или кто её выполнил

        completed   - время, когда задача была выполнена

    """
    order = models.ForeignKey(Order, related_name='queue')

    piece = models.ForeignKey(Piece, related_name='queue')

    audio_file = models.FileField(
        max_length=255,
        upload_to=upload_queue_path)

    price = models.ForeignKey(Price)

    TRANSCRIBE = 0
    EDIT = 1
    WORK_TYPE_CHOICES = (
        (TRANSCRIBE, 'Transcribe'),
        (EDIT, 'Check and edit')
    )
    work_type = models.IntegerField(
        choices=WORK_TYPE_CHOICES,
        default=TRANSCRIBE
    )

    priority = models.IntegerField(default=0)

    work_length = models.IntegerField(default=0)
    mistakes_length = models.IntegerField(default=0)

    locked = models.DateTimeField(null=True)
    skipped = models.IntegerField(default=0)

    owner = models.ForeignKey('auth.User',
                              blank=True,
                              null=True,
                              related_name='queue')
    completed = models.DateTimeField(null=True)
    checked   = models.DateTimeField(null=True)

    def __unicode__(self):
        return "%d: %d-%d sec" % (self.id, self.start_at, self.end_at)

    @property
    def pieces(self):
        if self.work_type == self.EDIT and self.piece.next != None:
            return [self.piece, self.piece.next]
        else:
            return [self.piece]

    @property
    def duration(self):
        return self.end_at - self.start_at

    @property
    def start_at(self):
        """
            Начала куска относительно всей записи
        """
        return np.round(self.piece.start_at)

    @property
    def end_at(self):
        """
            Конец куска относительно всей записи
        """
        # Если очередь на стенографирование,
        # то просто берём время окончания у связанного куска
        if self.work_type == self.TRANSCRIBE:
            return np.round(self.piece.end_at)

        # Если проверка, то провремя кусок в связке с соседним.
        elif self.work_type == self.EDIT:
            # Берём время, когда заканчивается кусок, следующий за текущим.
            next_piece = self.piece.next

            # TODO: Если следующего нет, то ничего не делаем.
            if not next_piece:
                return self.piece.end_at

            return np.round(
                next_piece.end_at
            )

    @property
    def offset_parts(self):
        parts = []

        # Если распознана предыдущая часть, даём три последних слова
        if self.piece.previous and self.piece.previous.transcriptions.count() > 0:
            last_transcription = self.piece.previous.transcriptions.all(
            ).last().text.split(" ")

            index = 0 if len(last_transcription) < 4 else len(
                last_transcription) - 5

            previous_part = " ".join(
                last_transcription[index:len(last_transcription)])
        else:
            previous_part = ""

        # Если распознана следующая часть, то даём три первых слова
        if self.pieces[-1].next and self.pieces[-1].next.transcriptions.count() > 0:
            last_transcription = self.pieces[-1].next.transcriptions.all().first().text.split(" ")

            index = len(last_transcription) if len(
                last_transcription) < 5 else 5

            next_part = " ".join(last_transcription[0:index])
        else:
            next_part = ""

        return (previous_part, next_part)

    @property
    def total_price(self):
        duration = self.end_at - self.start_at
        # TODO: загружать цену за прослушивание автоматически
        queue_object_id = ContentType.objects.get_for_model(type(self)).id
        price_listening = Price.objects.filter(content_type_id=queue_object_id, work_type=Price.WORK_TYPE_LISTENING, default=1)[0]

        if self.owner_id == 2:
            price_speeckit = Price.objects.filter(content_type_id=queue_object_id, work_type=Price.WORK_TYPE_TRANSCRIBE_SPEECHKIT, default=1)[0]
            return price_speeckit.price

        # Если очередь выполнена, считаем итоговоую цену
        if self.completed:
            total_price = (self.work_length - self.mistakes_length) * self.price.price

            # Если всё впорядке и это исправление, даём цену за прослушивание
            if total_price >= 0 and self.work_type == self.EDIT:
                total_price += price_listening.price * duration

            if total_price > 0:
                return total_price
            else:
                # Если много ошибался, испортил или не проверил
                return 0

        # Если проверка. То отдельно за прослушку и за каждое исправление
        if self.work_type == self.EDIT:
            return price_listening.price * duration

        # Если стенографирование, то считаем за символ
        if self.work_type == self.TRANSCRIBE:
            # return self.order.record.speed * self.price.price
            return 0

    @property
    def original_transcription(self):
        return "\n".join([t.text for t in self._get_trancriptions(version=-1)])

    @property
    def transcription(self):
        return "\n".join([t.text for t in self._get_trancriptions()])

    @property
    def checked_transcription(self):
        return "\n".join([t.text for t in self._get_trancriptions(version=1)])

    @property
    def _work_length(self):
        letters_count = self._diff_result(
            self.original_transcription,
            self.transcription, [1])

        return letters_count

    @property
    def _mistakes_length(self):
        if len(self.checked_transcription) == 0:
            return 0

        letters_count = self._diff_result(
            self.transcription,
            self.checked_transcription, [-1,])

        return letters_count

    def _get_trancriptions(self, version=0):
        # version - версия транскрибции. что было -1, что есть 0, что стало 1

        # Нужны транскрибции этой очереди, предыдущая, следующая для этих кусков
        if not self.completed:
            return []

        transcriptions = []

        for piece in self.pieces:
            # Определяем очереди, которые участвовали в проверке
            # Это очереди этого куска и очередь на проверку предыдущего.
            queue_ids = list(Queue.objects.\
                filter(piece_id=piece.id, completed__isnull=False).\
                values_list('id', flat=True).distinct())

            if piece.previous and piece.previous.check_transcription_queue.completed:
                queue_ids.append(piece.previous.check_transcription_queue.id)

            # Если версия предыдущая, берём первую транскрибцию из очереди младше
            if version == -1:
                queue = Queue.objects.filter(id__in=queue_ids, completed__lt=self.completed).order_by('completed')
                if len(queue) > 0:
                    queue = queue[0]
                else:
                    continue

            elif version == 0:
                queue = self
            elif version == 1:
                queue = Queue.objects.filter(id__in=queue_ids, completed__gt=self.completed).order_by('completed')
                if len(queue) > 0:
                    queue = queue[0]
                else:
                    queue = self

            # Выдаём транскрибцию
            transcriptions += piece.all_transcriptions.filter(
                queue=queue).order_by('index')

        return transcriptions

    def _diff_result(self, original_transcription, transcription, diff_type=[1,-1]):
        d = diff_match_patch()

        # Сколько заработали на нём
        diff = d.diff_main(original_transcription, transcription)
        d.diff_cleanupSemantic(diff)

        letters_count = 0
        for work in diff:
            if work[0] in diff_type:
                letters_count += len(work[1])

        # Берём предыдущую транскрибцию по времени и сравниваем
        # Если есть следующая транскрибция, считаем разницу и вычитаем из предыдущей
        return letters_count

    def update_work_metrics(self):
        self.work_length = self._work_length
        self.mistakes_length = self._mistakes_length

        if self.checked:
            return

        # Если проверен кусок, помечаем как проверенную
        for piece in self.pieces:
            for queue in piece.queue.all():
                if not queue.completed:
                    return

        self.checked = datetime.now()

        self.save()

    def update_payments(self):
        # Для всех задач учавствовавших в транскрибации куска делаем перерасчёт
        queues_id = self.piece.all_transcriptions.values('queue_id').distinct()
        queues = Queue.objects.filter(id__in=queues_id).order_by('completed')

        for queue in queues:
            queue.update_work_metrics()
            queue.save()

            # payment = Payment.objects.for_model(Queue).filter(object_pk==queue.id)
            type_id = ContentType.objects.get_for_model(type(queue)).id
            payment = Payment.objects.get(content_type_id=type_id, object_id=queue.id)

            if payment:
                # Обновляем показатели бабла
                # diff = payment.total - queue.total_price
                payment.total = queue.total_price

                # queue.owner.account.balance += diff

                payment.save()
                # queue.owner.account.save()

    def update_priority(self):
        """
            Меняем приоритет следующего куска на высокий,
            и о вычитки этого куска, если транскрибцию выполнили в соседних.
        """
        # Делаем следующий кусок приоритетным, если необходимо
        next_queue = Queue.objects.filter(
            piece=self.piece.next, priority=0, work_type=0).first()

        if next_queue:
            next_queue.priority = 2
            next_queue.save()

        # Проверяем готовы ли окружающие куски
        # Если готовы, то отправляем их на проверку
        pieces_blocks = []

        if self.piece.previous:
            pieces_blocks.append((self.piece.previous.id, self.piece.id))
        if self.piece.next:
            pieces_blocks.append((self.piece.id, self.piece.next.id))

        for pieces in pieces_blocks:
            # Ищем выполненные очереди транскрибции
            completed_pieces = Queue.objects.filter(
                piece__id__in=pieces, work_type=0, completed__isnull=False)

            check_queue = Queue.objects.get(piece_id=pieces[0], work_type=1)

            # Если очереди готовы и этот кусок уже не проверен
            # Повышаем его в приоритете
            if completed_pieces.count() == 2 and check_queue.priority == 0:
                check_queue.priority = 2
                check_queue.save()

    def audio_file_make(self, as_record=None, offset=0):
        """
            Создаёт вырезанный кусок в mp3

            offset  - сколько записи по краям оставлять
        """
        from django.core.files import File

        # Если запись уже создана, возвращаем название файла
        if self.audio_file:
            return self.audio_file_local()

        audio_file_path = self.piece.record.cut_to_file(
            as_record=as_record,
            file_name=upload_queue_path(self),
            start_at=self.start_at,
            end_at=self.end_at,
            offset=offset
        )

        # Сохраняем на Амазон с3
        self.audio_file.delete()
        self.audio_file.save(
            audio_file_path,
            File(
                open(settings.MEDIA_ROOT + audio_file_path)
            )
        )

        return audio_file_path

def create_queue_payment(sender, instance, created, raw, using, update_fields, **kwargs):
    # Берём дефолтный прайс для объекта
    if not instance.completed:
        return

    # Если есть платёж, новый не создаём
    try:
        type_id = ContentType.objects.get_for_model(type(instance)).id
        payment = Payment.objects.get(content_type_id=type_id, object_id=instance.id)
        return
    except Payment.DoesNotExist:
        pass

    # TODO: Если платёж по этому объекту уже есть, то ничего не делать

    owner = instance.owner

    price = instance.price

    total = instance.total_price

    payment = Payment(
        content_object=instance,
        price=price,
        total=total,
        owner=owner)

    payment.save()
    owner.account.save()

# register the signal
signals.post_save.connect(create_queue_payment, sender=Queue)

