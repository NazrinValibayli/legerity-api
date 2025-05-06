docker-compose run --rm app sh -c "django-admin startproject app ."
docker-compose run --rm app sh -c 'python manage.py startapp helpers'
docker compose run --rm app sh -c 'python manage.py wait_for_db'
docker-compose -f docker-compose-deploy.yml down
docker-compose -f docker-compose-deploy.yml build
docker-compose -f docker-compose-deploy.yml up
Command to create secret key for settings.py
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
python -c 'from secrets import token_hex; print(token_hex(16))'
Command to remove unused data
docker system prune
