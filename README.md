# I-Manual Masterbot Demo

## Launch QA API

QA api server 실행

```bash
opyrator launch-api app:question_answering
```

## Build QA data with train dataset

finetune에 사용한 train data의 결과를 json에 저장

```bash
python build_qa_data.py --model mbert
python build_qa_data.py --model koelectra
```
