FROM python:3-slim
RUN apt-get update && apt-get install -y ffmpeg

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY gentleman_bot.py .
CMD ["python", "gentleman_bot.py"]
