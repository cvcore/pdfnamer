# PDFNamer

Automatically rename PDFs by extracting titles using OpenAI API and OCR via Docker.

## Quick Start

Run the Docker container:

```bash
docker run -e OPENAI_API_KEY='sk--xxxxxxxxx' \
           -e INPUT_FOLDER='/pdf_input' \
           -e OUTPUT_FOLDER='/pdf_output' \
           -v /host_directory/pdf_input:/pdf_input \
           -v /host_directory/pdf_output:/pdf_output \
           cvcore/pdfnamer:latest
```

It assumes the pdf files are located in `/host_directory/pdf_input` and are named as `YYYYMMDD_filename.pdf`. The renamed files will be saved in `/host_directory/pdf_output` with the format `YYYYMMDD_title.pdf`.

## Prerequisites

- Docker: Ensure Docker is installed.
- OpenAI API Key: Obtain from [OpenAI](https://platform.openai.com/api-keys).

## Environment Variables

- OPENAI_API_KEY: Your OpenAI API key.
- INPUT_FOLDER: Directory inside the container where PDFs are read from.
- OUTPUT_FOLDER: Directory inside the container where renamed PDFs are saved.


## Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run the script: `python your_script.py`

## License

Licensed under the MIT License.
