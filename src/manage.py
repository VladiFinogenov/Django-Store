#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megano.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't product_import Django. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

from hh.models import AdvUser
from re_action.utilities import send_balance_notification

user = AdvUser.objects.create_user(
    username='testuser',
    email='Finogenov.V.A@yandex.ru',
    password='Volgograd@2024'
)
user.save()

class ResumeSJ:
    def __init__(self, user):
        self.user = user

class ResumeZP:
    def __init__(self, user):
        self.user = user

class ResumeHH:
    def __init__(self, user):
        self.user = user

resume_sj = ResumeSJ(user)
resume_zp = ResumeZP(user)
resume_hh = ResumeHH(user)

class Operation:
    def __init__(self, resume):
        self.resume = resume

operations_sj = [Operation(resume_sj) for _ in range(30)]
operations_zp = [Operation(resume_zp) for _ in range(30)]
operations_hh = [Operation(resume_hh) for _ in range(30)]

send_balance_notification(user)




import os

from django.conf import settings
from django.conf import settings as s
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.template.loader import render_to_string
from hh.management.commands.send_responses_command import Command
# Импортируем модель пользователя или резюме
from hh.models import Accounting, AdvUser, Resume

# Пример удаления резюме, связанных с пользователем
# resume_sj.get(email='Finogenov.V.A@yandex.ru')
for item in Accounting.objects.values('user__pk').annotate(sum=Sum('amount')). \
        order_by('sum').filter(sum__gt=s.LETTER_PRICE):

    user = AdvUser.objects.get(pk=item['user__pk'])
    resumes = ResumeZP.objects.filter(
        user__pk=item['user__pk'], startSending=True)

    for resume in resumes:
        resume.delete()

    subject = ('account/email/user_deleted_resume_subject.txt').strip()
    body_html = ('account/email/user_deleted_resume_message.html',
                 {'job_site': 'HH.ru'})
    user.email_user(
        subject=subject,
        html_message=body_html,
    )

# Создание экземпляра команды
cmd = Command()

# Выполнение метода handle
cmd.handle()



import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.template.loader import render_to_string
from hh.models import (Accounting,  # Замените myapp на имя вашего приложения
                       AdvUser, Operation, ResumeSJ, SendingReciept)
from re_action.HHApi import (AccessForbidden, BadRequest,
                             SearchRequestNotFound, UnknownError)
from re_action.SJApi import SJApiInteraction

logger = logging.getLogger(__name__)

class SearchRequestNotFound(Exception):
    pass

class Command(BaseCommand):
    help = 'Команда для управления рассылкой резюме и обработки ошибок поиска'

    def handle(self, *args, **kwargs):
        logger.info('вызов метода handle command sj')
        end_time = datetime.now() + timedelta(minutes=55)

        for item in Accounting.objects.values('user__pk').annotate(sum=Sum('amount')).order_by('sum').filter(sum__gt=settings.LETTER_PRICE):
            try:
                user = AdvUser.objects.get(pk=item['user__pk'])
                self.raise_balance_over(balance=item['sum'], user=user)
                resumes = ResumeSJ.objects.filter(user__pk=item['user__pk'], startSending=True)

                for resume in resumes:
                    receipt = SendingReceipt()
                    try:
                        self.resume_sending(
                            user=user,
                            item=item,
                            resume=resume,
                            receipt=receipt,
                            end_time=end_time
                        )
                    except SearchRequestNotFound:
                        receipt.status = SendingReceipt.SEARCH_NOT_FOUND
                        logger.exception('Search Request Not Found: %s', resume.search_id)
                        resume.search_id = ''
                        resume.search_url_name = 'УДАЛЕН'
                        resume.startSending = False
                        resume.save()
                        user.email_user(
                            subject='Re-Action: рассылка приостановлена',
                            message=f'{user.username} добрый день!'
                                    'Робот не может найти ваш поисковой запрос. Возможно, он был удален на джоб сайте.'
                                    'Пожалуйста, создайте новый / или выберите уже готовый запрос в ваших настройках.'
                                    'Чтобы возобновить рассылку, перейдите в сервис и настроите рассылку повторно '
                                    'с новым поисковым запросом. '
                                    'Возникли проблемы с переходом по ссылке? Свяжитесь со Службой поддержки '
                                    'https://t.me/avgrudin '
                                    'Команда Re-Action',
                            from_email=settings.DEFAULT_FROM_EMAIL
                        )

            except Exception as e:
                logger.error(f"Error processing user {item['user__pk']}: {str(e)}")

        self.stdout.write(self.style.SUCCESS('Finished processing resumes'))

    def resume_sending(self, user, item, resume, receipt, end_time):
        # Логика отправки резюме
        # Имитация ошибки
        raise SearchRequestNotFound("Search request not found")
        # Если ошибок нет, продолжить выполнение и обновить статус на SUCCESS
        receipt.status = SendingReceipt.SUCCESS
        receipt.save()
# Создание экземпляра команды
cmd = Command()

# Выполнение метода handle
cmd.handle()
