FROM python:3.11-alpine

RUN apk add --no-cache ffmpeg

COPY ./ ./

COPY ./main.py ./app.py

RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "app:app", "--host=0.0.0.0", "--port=5000","--reload"]
