FROM sehandev/lambda-stack:20.04
MAINTAINER Sehan Kim <sehandev@gmail.com>

COPY . /workspace
WORKDIR /workspace

RUN ["pip", "install", "-r", "requirements.txt"]

RUN ["python", "build_qa_data.py", "--model", "mbert"]
RUN ["python", "build_qa_data.py", "--model", "koelectra"]

CMD ["opyrator", "launch-api", "app:question_answering"]