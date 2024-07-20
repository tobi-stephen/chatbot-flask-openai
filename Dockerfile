FROM python:alpine

WORKDIR /chatbot
ADD app.py app.py
ADD utils.py utils.py
ADD /templates templates

RUN apk upgrade --no-cache && \
    apk add --no-cache bash openssl libgcc libstdc++ ncurses-libs

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir flask openai requests python-dotenv beautifulsoup4 pymupdf langchain langchain_openai

EXPOSE 5000

CMD [ "flask", "run", "--host", "0.0.0.0", "--debug" ]
