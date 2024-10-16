# Use the official Alpine Linux image with Python 3.12
FROM python:3.12-alpine

RUN apk update && apk add --no-cache \
    build-base \
    libjpeg-turbo-dev \
    zlib-dev \
    poppler-utils \
    tiff-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    libimagequant-dev \
    libwebp-dev \
    harfbuzz-dev \
    fribidi-dev \
    leptonica-dev \
    tesseract-ocr \
    tesseract-ocr-data-eng \
    && pip install --upgrade pip \
    && apk add --no-cache tiff-dev freetype-dev lcms2-dev openjpeg-dev libimagequant-dev libwebp-dev harfbuzz-dev fribidi-dev

COPY ./pdfnamer /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "/app/pdfnamer.py"]
