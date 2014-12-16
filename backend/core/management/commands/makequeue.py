#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from backend.order.models import *

from pydub import AudioSegment


class Command(BaseCommand):
    args = '<issue_id issue_id ...>'
    help = 'Import the specified participant from jira'
    # Количество неудачных попыток импортировать следующие записи, после
    # которого импорт прекратиться.
    not_exists_tries = 5

    def handle(self, *args, **options):
        # Берём все заказы, где записи не распознаны

        # Создаём очередь на рапознание через один
        # Потом, когда созданны. Пробегаемся и изменяем или создаём
        # приоритетные, которые следующие после распознанные.
        orders = Order.objects.filter(record__progress=1)

        for order in orders:
            rec_mp3 = AudioSegment.from_mp3(
                settings.RECORD_ROOT +
                order.record.file_name_format('mp3')
            )
            transcribe_object_id = ContentType.objects.get_for_model(Piece).id
            transcribe_price = Price.objects.filter(
                content_type_id=transcribe_object_id, default=1)[0]

            check_object_id = ContentType.objects.get_for_model(Transcription).id
            check_price = Price.objects.filter(
                content_type_id=check_object_id, default=1)[0]


            # Если нет очереди, создаём для каждого чётного куска
            if order.queue_set.count() == 0:
                print "Create queue for order %d" % order.id

                for index, piece in enumerate(order.record.piece_set.all().order_by('start_at')):
                    if index % 2 == 0:
                        queue = Queue(
                            order=order,
                            piece=piece,
                            price=transcribe_price,
                            work_type=0)

                        self.make_mp3(
                            rec=rec_mp3,
                            path=queue.mp3_path(),
                            start_at=queue.start_at(),
                            end_at=queue.end_at())

                        queue.save()

            else:
                # Если уже есть части в очереди
                for piece in order.record.piece_set.all().order_by('start_at'):
                    # Если у текущего куска, уже есть транскрипция, то
                    # добавляем или изменяем приоритет в очереди
                    next_piece = Piece.objects.filter(
                        start_at__gte=piece.end_at).order_by('start_at')[0]

                    if piece.transcription_set.count() > 0:
                        try:
                            queue = Queue.objects.get(piece=next_piece)

                            # Если следующая запись тоже написана, создаём очередь на проверку,
                            # если её
                            if queue.completed:
                                try:
                                    check_queue = Queue.objects.get(
                                        piece=piece, work_type=1)
                                except Queue.DoesNotExist:
                                    check_queue = Queue(
                                        order=order,
                                        piece=piece,
                                        price=check_price,
                                        work_type=1,
                                        priority=True)

                                    self.make_mp3(
                                        rec_mp3,
                                        check_queue.mp3_path(),
                                        check_queue.start_at(),
                                        check_queue.end_at()
                                        )
                                    check_queue.save()

                        except Queue.DoesNotExist:
                            queue = Queue(
                                order=order,
                                piece=next_piece,
                                price=transcribe_price,
                                work_type=0,
                                priority=True)

                            self.make_mp3(
                                rec_mp3, queue.mp3_path(), queue.start_at(), queue.end_at())

                            queue.save()

    def make_mp3(self, rec, path, start_at, end_at, offset=1.5):
        if not os.path.isfile(settings.RECORD_ROOT + path):
            piece = rec[
                ((start_at - offset) * 1000):
                ((end_at + offset) * 1000)
            ]
            piece.export(settings.RECORD_ROOT + path)
