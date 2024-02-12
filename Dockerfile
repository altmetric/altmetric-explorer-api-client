FROM python:3.10.12

WORKDIR /app

COPY lib/qa/requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . ./
