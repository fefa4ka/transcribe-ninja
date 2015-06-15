#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.files import File

from django_rq import job

from work.models import *

from transcribe.models import *

from pydub import AudioSegment


@job('prepare')
def record_prepare(record):
    # Сперва подготавливаем запись
    record.prepare()
    record.save()

    # Потом асихронно анализируем.
    # Подготовка происходит быстро,
    # и чтобы не задерживать другие подготовки,
    # анализ делаем в другой очереди
    record_analys.delay(record)


@job('analys')
def record_analys(record):
    record.diarization()

    if record.progress == 1:
        order = record.order.all()[0]
        make_queue.delay(order)

    record.progress = 2
    record.save()


@job('queue')
def update_near(queue):
    queue.update_priority()
    queue.update_payments()


@job('queue')
def make_queue(order):
    # TODO: Пока не диаризируется, не создавать очередь
    if order.record.progress == 2:
        order.make_queue()
        order.record.recognize()

    order.record.progress = 3
    order.record.save()

# @job('transcribe')

    # Берём все заказы, где записи не распознаны

    # Создаём очередь на рапознание через один
    # Потом, когда созданны. Пробегаемся и изменяем или создаём
    # приоритетные, которые следующие после распознанные.

    # Скачиваем эмпэтришку с Амазон С3, во временную папку
    # s3_record_file = order.record.file_name
    # record_file_name = str(s3_record_file)

    # s3_record_file.open()
    # mp3_data = s3_record_file.read()

    # mp3_file_path = settings.TEMP_DIR + record_file_name
    # if not os.path.exists(mp3_file_path):
    #     os.makedirs(os.path.dirname(mp3_file_path))
    # mp3_file = open(
    #     mp3_file_path,
    #     'w+')
    # mp3_file.write(mp3_data)
    # mp3_file.close()

    # # Загружаем эмпэтришку, черезе AudioSegment для нарезки
    # record = AudioSegment.from_mp3(
    #     settings.TEMP_DIR + record_file_name
    # )

    # # Цена по умолчанию за транскрибцию
    # transcribe_object_id = ContentType.objects.get_for_model(Piece).id
    # transcribe_price = Price.objects.filter(
    #     content_type_id=transcribe_object_id,
    #     default=1
    # )[0]

    # # Цена по умолчанию за вычитку
    # check_object_id = ContentType.objects.get_for_model(Transcription).id
    # check_price = Price.objects.filter(
    #     content_type_id=check_object_id,
    #     default=1
    # )[0]

    # # Создаём заявки на транскрибцию каждого куска
    # # Кажный нечётный - приоритетный
    # for index, piece in enumerate(order.record.piece_set.all().order_by('start_at')):
    #     queue = Queue(
    #         order=order,
    #         piece=piece,
    #         price=transcribe_price,
    #         priority=False if index % 2 == 0 else True,
    #         work_type=Queue.TRANSCRIBE)

    #     # Вырезаем нужный кусок записи
    #     offset = 1.5
    #     piece_mp3 = record[
    #         ((queue.start_at() - offset) * 1000):
    #         ((queue.end_at() + offset) * 1000)
    #     ]
    #     # Сохраняем его на Амазон С3
    #     piece_mp3_file_name = upload_queue_path(queue, record_file_name)
    #     piece_mp3_path = settings.TEMP_DIR + piece_mp3_file_name
    #     piece_mp3.export(piece_mp3_path)

    #     if not os.path.exists(piece_mp3_path):
    #         os.makedirs(os.path.dirnames(piece_mp3_path))
    #     piece_mp3 = open(piece_mp3_path)

    #     queue.file_name.save(piece_mp3_file_name, File(piece_mp3_path))

#     # Если нет очереди, создаём для каждого чётного куска
#     if order.queue_set.count() == 0:
#         for index, piece in enumerate(order.record.piece_set.all().order_by('start_at')):
#             if index % 2 == 0:
#                 queue = Queue(
#                     order=order,
#                     piece=piece,
#                     price=transcribe_price,
#                     work_type=0)

#                 self.make_mp3(
#                     rec=rec_mp3,
#                     path=queue.mp3_path(),
#                     start_at=queue.start_at(),
#                     end_at=queue.end_at())

#                 queue.save()

#     else:
#         # Если уже есть части в очереди
#         for piece in order.record.piece_set.all().order_by('start_at'):
#             # Если у текущего куска, уже есть транскрипция, то
#             # добавляем или изменяем приоритет в очереди
#             next_piece = Piece.objects.filter(
#                 start_at__gte=piece.end_at).order_by('start_at')[0]

#             if piece.transcription_set.count() > 0:
#                 try:
#                     queue = Queue.objects.get(piece=next_piece)

#                     # Если следующая запись тоже написана, создаём очередь на проверку,
#                     # если её
#                     if queue.completed:
#                         try:
#                             check_queue = Queue.objects.get(
#                                 piece=piece, work_type=1)
#                         except Queue.DoesNotExist:
#                             check_queue = Queue(
#                                 order=order,
#                                 piece=piece,
#                                 price=check_price,
#                                 work_type=1,
#                                 priority=True)

#                             self.make_mp3(
#                                 rec_mp3,
#                                 check_queue.mp3_path(),
#                                 check_queue.start_at(),
#                                 check_queue.end_at()
#                             )
#                             check_queue.save()

#                 except Queue.DoesNotExist:
#                     queue = Queue(
#                         order=order,
#                         piece=next_piece,
#                         price=transcribe_price,
#                         work_type=0,
#                         priority=True)

#                     self.make_mp3(
#                         rec_mp3, queue.mp3_path(), queue.start_at(), queue.end_at())

#                     queue.save()


# def make_mp3(self, rec, path, start_at, end_at, offset=1.5):
#     if not os.path.isfile(settings.RECORD_ROOT + path):
#         piece = rec[
#             ((start_at - offset) * 1000):
#             ((end_at + offset) * 1000)
#         ]
#         # piece.export(settings.RECORD_ROOT + path)

#         return piece
