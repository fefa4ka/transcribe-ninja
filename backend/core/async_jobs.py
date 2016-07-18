#!/usr/bin/python
# -*- coding: utf-8 -*-

from django_rq import job

from transcribe.models import *

from work.models import *

from django.db.models import Q

from dbmail import send_db_mail

# Очереди для записей

@job('prepare', timeout=3600)
def record_prepare(record):
    """
        Очередь на подготовку

        Подготовка записи для системы
        Конвертирует в mp3

        record — экземляр записи Record
    """
    # Если не перезагрузить объект, то при сохранении будет (2006, 'MySQL server has gone away')
    record = Record.objects.get(id=record.id)

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

def invite_workers():
    # Определяем срок выполнения задачи
    # Среднюю скорость на человека
    # Скорость в последний час
    # Прогнозируем
    pass

# Очереди для очереди
@job('make_queue', timeout=18000)
def make_queue(order):
    """
        Очередь на создание очереди
        на распознание

        order - экземпляр класса заказа Order
    """
    # Пока не диаризируется, не создавать очередь
    order = Order.objects.get(id=order.id)
    if order.record.progress >= Record.PROGRESS_DIARIZED:
        order.record.progress = Record.PROGRESS_INWORK
        order.record.save()

        # Создаём очередь
        order.make_queue()
        # Распознаём
        # TODO: Запускать отдельной очередью
        # order.record.recognize()

        # Приглашаем людей на сайт
    else:
        # TODO: потенциальный баг
        order.record.progress = Record.PROGRESS_ORDERED

    order.record.save()


@job('update_queue')
def update_near(queue):
    """
        Результат работы каждого зависит от того,
        как другие другие выполнят свою работу.

        После выполнение очереди, обновляем данные
        в связанных очередях.

        queue - экземпляр класса очереди Queue

    """
    queue = Queue.objects.get(id=queue.id)

    record = queue.order.record

    queue.update_priority()
    queue.update_payments()

    # Если вся задача выполнена, помечаем её как проверенную
    # автоматически редактируем текст и отправляем его на проверку
    for order in record.orders.all():
        if order.queue.filter(completed__isnull=True).count() == 0:
            record.status = 4
            record.save()
            export_transcription.delay(record)

    # Если у мудака рейтинг плохой — блочим
    account = queue.owner.account
    account.rating = account.actual_rating
    account.save()

    if account.rating < 0.5:
        queue.owner.active = 0
        queue.owner.save()

        # Отправляем письмо о блокировке
        if queue.owner.email:
            send_db_mail('ninja-block', queue.owner.email)


@job('update_queue')
def flush_user_work(user):
    """
        Удаляем всю работу пользователя и выставляем её на проверку
    """
    # Пробегаемся по очередям и удаляем: транскрибции, платежи, сбрасываем время выполнения, проверки и блокировку.

    queues = user.queue
    empty_queues = queues.filter(Q(work_length=0) | Q(checked__isnull=True))

    for queue in empty_queues:
        queue.transcriptions.all().delete()
        queue.payment.delete()

        queue.completed = None
        queue.checked = None
        queue.locked = None
        queue.owner_id = None
        queue.save()

        update_near.delay(queue)



@job('prepare', timeout=3600)
def export_transcription(record):
    """
        Экспортируем транскрибцию в разные форматы

        record - экземпляр класса записи Record
    """
    formats = ['doc', 'xls', 'srt', 'txt']

    for ext in formats:
        export = Export(record_id=record.id, file_format=ext)
        export.generate_file()
        export.save()
