#!/usr/bin/python
# -*- coding: utf-8 -*-

from django_rq import job

from transcribe.models import *

from work.models import *

# Очереди для записей

@job('prepare', timeout=3600)
def record_prepare(record):
    """
        Очередь на подготовку

        Подготовка записи для системы
        Конвертирует в mp3

        record — экземляр записи Record
    """
    # Сперва подготавливаем запись
    record.prepare()
    record.save()

    # Потом асихронно анализируем.
    # Подготовка происходит быстро,
    # и чтобы не задерживать другие подготовки,
    # анализ делаем в другой очереди
    record_analys.delay(record)


@job('analys', timeout=18000)
def record_analys(record):
    """
        Очередь на диаризацию

        В результате помечаем запись как диаризованную.

        Если был заказ, то запись отправляет на создание очереди на распознание.

        record — экземляр записи Record
    """
    # Диаризируем
    record.diarization()

    # Обновляем данные. Процесс был долгий, могло всё измениться
    record = Record.objects.get(id=record.id)
    orders = record.orders.all()

    # Обновляем данные о записи
    record.progress = Record.PROGRESS_DIARIZED
    record.save()

    # Запускаем очереди на распознание, если неужно
    for order in orders:
        make_queue.delay(order)


# @job('mail', timeout=4600)
# def work_notifications():
#     yesterday = datetime.date.fromordinal(datetime.date.today().toordinal()-1)
#     seconds_per_day = sum(q.duration for q in Queue.objects.filter(completed__gt=yesterday))
#     seconds_uncompleted = sum(q.duration for q in Queue.objects.filter(completed__isnull=True))

#     # Если с такой скоростью весь объём не распознаем
#     if seconds_uncompleted/seconds_per_day > 1;


# Очереди для очереди
@job('prepare', timeout=3600)
def make_queue(order):
    """
        Очередь на создание очереди
        на распознание

        order - экземпляр класса заказа Order
    """
    # Пока не диаризируется, не создавать очередь
    if order.record.progress == Record.PROGRESS_DIARIZED:
        order.record.progress = Record.PROGRESS_INWORK
        order.record.save()

        # Создаём очередь
        order.make_queue()
        # Распознаём
        # TODO: Запускать отдельной очередью
        # order.record.recognize()
    else:
        order.record.progress = Record.PROGRESS_ORDERED

    order.record.save()


@job('queue')
def update_near(queue):
    """
        Результат работы каждого зависит от того,
        как другие другие выполнят свою работу.

        После выполнение очереди, обновляем данные
        в связанных очередях.

        queue - экземпляр класса очереди Queue

    """
    record = queue.order.record

    queue.update_priority()
    queue.update_payments()

    # Если вся задача выполнена, помечаем её как проверенную

    for order in record.orders.all():
        if order.queue.filter(completed__isnull=True).count() == 0:
            record.status = 4
            record.save()
            export_transcription.delay(record)


@job('prepare', timeout=3600)
def export_transcription(record):
    """
        Экспортируем транскрибцию в разные форматы

        record - экземпляр класса записи Record
    """
    formats = ['xls', 'srt', 'txt']

    for ext in formats:
        export = Export(record_id=record.id, file_format=ext)
        export.generate_file()
        export.save()
