# I-Manual Masterbot Demo

<img src="https://github.com/sehandev/masterbot-demo/blob/main/example.png?raw=true" width="1024" />

## Launch QA API

QA api server 실행

```bash
opyrator launch-api app:question_answering
```

### request

model_name: 사용할 finetuned model 이름 (mbert, koelectra, tfidf)

context: 해당하는 paragraph

question: 질문

### response

answer: 답변

## Build QA data with train dataset

finetune에 사용한 train data의 결과를 json에 저장

```bash
python build_qa_data.py --model mbert
python build_qa_data.py --model koelectra
python build_qa_data.py --model tfidf
```
