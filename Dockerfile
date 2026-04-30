FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG SECRET_KEY
ARG TMDB_API_KEY
ARG DEBUG=False
ARG ALLOWED_HOSTS=localhost,127.0.0.1
ARG CSRF_TRUSTED_ORIGINS=

ENV SECRET_KEY=${SECRET_KEY}
ENV TMDB_API_KEY=${TMDB_API_KEY}
ENV DEBUG=${DEBUG}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
ENV CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "MyMovies.wsgi:application", "--bind", "0.0.0.0:8000"]
