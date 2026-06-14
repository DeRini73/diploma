#!/bin/bash
echo '---------------------------'
echo '|      ЗАПУСК ТЕСТОВ      |'
echo '---------------------------'
python manage.py test diplom.tests -v 2
echo ''
echo '---------------------------'
echo '|         ОТЧЁТ           |'
echo '---------------------------'
coverage run --source='.' manage.py test diplom.tests -v 0
coverage report -m
echo ""
echo "ТЕСТИРОВАНИЕ ЗАВЕРШЕНО"