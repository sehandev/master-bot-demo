import json
import argparse
from pathlib import Path

from tqdm import tqdm
from transformers import pipeline

from util import QuestionAnswering
from tfidf import Tfidf_QA_Module


PROJECT_DIR = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_DIR / 'data'

MODEL_DICT = {
    'mbert': 'songhee/i-manual-mbert',
    'koelectra': 'mtr0930/koelectra-base-v3_epoch-100',
    'tfidf': 'mtr0930/i-manual_tokenizer_updated',
}


def load_data():
    with open(DATA_DIR / 'i-manual_train.json') as dataset_file:
        dataset_json = json.load(dataset_file)
        dataset = dataset_json['data']

    return dataset


def save_result(model_name: str, result: dict):
    # Prod
    with open(f'./front/public/{model_name}.json', 'w', encoding='UTF-8') as result_file:
        result_file.write(json.dumps(result, ensure_ascii=False))

    # Dev
    with open(DATA_DIR / f'{model_name}-pretty.json', 'w', encoding='UTF-8') as result_file:
        result_file.write(json.dumps(result, ensure_ascii=False, indent=4))


def answer_data(nlp, data):
    result_dict = {}
    for article in tqdm(data):
        title = article['title']
        result_dict[title] = []

        for paragraph in article['paragraphs']:
            context = paragraph['context']

            content = {
                'context': context,
                'qas': [],
            }

            for qa in paragraph['qas']:
                question = qa['question']
                answer = nlp(context=context, question=question)['answer']

                content['qas'].append({
                    'id': qa['id'],
                    'question': question,
                    'answer': answer.replace('[UNK]', '...'),
                })

            result_dict[title].append(content)

    return result_dict


def main(model_name):
    nlp = QuestionAnswering(MODEL_DICT[model_name])
    data = load_data()

    result = answer_data(nlp, data)
    save_result(model_name, result)


def build_tfidf_data(model_name):
    tfidf_module = Tfidf_QA_Module(MODEL_DICT[model_name])
    data = load_data()

    with open(DATA_DIR / 'tfidf.json', 'r', encoding='utf-8') as reader:
        tfidf_contexts = json.load(reader)['data']

    result_dict = []
    for article in tqdm(data):

        for paragraph in article['paragraphs']:
            context = paragraph['context']

            for qa in paragraph['qas']:
                question = qa['question']
                answer, matched_context = tfidf_module.get_answer(dataset=tfidf_contexts, question=question)

                result_dict.append({
                    'question': question,
                    'context': matched_context,
                    'answer': answer.replace('[UNK]', '...'),
                })

    save_result(model_name, result_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='train data의 결과를 미리 저장')
    parser.add_argument('--model', type=str, help='mbert, koelectra, tfidf', required=True)

    args = parser.parse_args()

    if args.model == 'tfidf':
        build_tfidf_data(args.model)
    else:
        main(args.model)
