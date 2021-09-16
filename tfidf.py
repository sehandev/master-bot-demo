from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import pandas as pd
import numpy as np
import argparse
from transformers import AutoConfig
import torch
import json


def remove_white_space(answer):
    if not answer:
        return answer

    # 작은 따옴표의 개수에 따라 시작 위치 변경
    toggle_c = answer.count("'")

    if toggle_c and toggle_c % 2 == 0:  # 짝수개일 경우 시작부분부터 시작  카운트
        toggle = True
    else:
        toggle = False  # 홀수개일 경우 끝부분부터 시작 카운트

    tokens = answer.split()
    l_space = ["‘"]  # 다음 토큰에 붙어야 하는 토큰
    r_space = [",", ".", "!", "?", "’", ")", "~", "%"]  # 이전 토큰에 붙어야하는 토큰
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    n_space = ["(", "/"]  # 앞뒤 토큰 모두 붙어야 하는 토큰
    length = len(tokens)

    result = []
    result.append(tokens[0])
    l_s = False

    for i in range(1, length):

        # 앞 뒤로 다 붙어야 하는 경우
        if (tokens[i - 1] == "'" and toggle) or (tokens[i - 1] == ")" and len(tokens[i]) == 1):
            result[-1] = result[-1] + tokens[i]
            continue

        if tokens[i] in n_space or (tokens[i - 1] == "." and tokens[i] in numbers):
            result[-1] = result[-1] + tokens[i]
            l_s = True
            continue

        # 다음 토큰에 붙어야 하는 경우
        if tokens[i] in l_space or (tokens[i] == "'" and toggle):
            l_s = True

            result.append(tokens[i])

            if tokens[i] == "'":
                toggle = False

            continue

        # 앞 토큰에 붙어야 하는 경우
        if tokens[i] in r_space or l_s or (tokens[i] == "'" and toggle == False):
            result[-1] = result[-1] + tokens[i]
            l_s = False

            if tokens[i] == "'":
                toggle = True
            continue

        result.append(tokens[i])

    return " ".join(result)


class Tfidf_QA_Module():
    """I-manual question answering class.
    Attributes:
        model (AutoModelForQuestionAnswering): transformers model.
        tokenizer (AutoTokenizer): transformers tokenizer.
        pipeline (QuestionAnsweringPipeline): transformers pipeline.
    """

    def __init__(self, pretrained_model_name_or_path=None):
        """Inits QuestionAnswering, and load a pre-trained model.
         Args:
            pretrained_model_name_or_path (str):
                Pretrained huggingface model name or model path.
        """

        self.config = AutoConfig.from_pretrained(
            pretrained_model_name_or_path)
        # KoELECTRA 의 경우 model load 에 return_dict = False 필요
        # m-BERT 사용하려면 아래 주석처리된 코드 이용
        self.model = AutoModelForQuestionAnswering.from_pretrained(
            pretrained_model_name_or_path,
            return_dict=False)
        # m-BERT
        # self.model = AutoModelForQuestionAnswering.from_pretrained(
        #     pretrained_model_name_or_path,
        #     config=self.config)
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path)

    def dummy(self, doc):
        return doc

    # 질문의 token 중 불용어 제거
    def custom_tokenize(self, tokens):
        question_inputs = self.tokenizer(tokens, add_special_tokens=False, return_tensors="pt")
        question_input_ids = question_inputs["input_ids"].tolist()[0]
        question_tokens = self.tokenizer.convert_ids_to_tokens(question_input_ids)

        my_text_tokens = []

        for tmp_token in question_tokens:
            if tmp_token != '.' and tmp_token != ',' and tmp_token != "'" and tmp_token != '?':
                my_text_tokens.append(tmp_token)

        return my_text_tokens

    # 126개의 paragraph 들과 질문을 입력으로 받아서
    # tf-idf score 가 가장 높은 paragraph 를 return 해줌.
    def tfidf(self, paragraphs, question):
        tokenized_texts = []

        for text in paragraphs:
            inputs = self.tokenizer(text, add_special_tokens=False, return_tensors="pt")
            input_ids = inputs["input_ids"].tolist()[0]
            text_tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
            tokenized_texts.append(text_tokens)

        stop_words = [",", "?", "!", ".", "'"]
        vect = TfidfVectorizer(max_features=10000, tokenizer=self.dummy, preprocessor=self.dummy, stop_words=stop_words)
        tfidf = vect.fit_transform(tokenized_texts)  # 문서-단어 행렬
        tf = pd.DataFrame(tfidf.toarray(), columns=vect.get_feature_names())
        feature_names = vect.get_feature_names()
        tokenized_question = self.custom_tokenize(question)

        one_coded_list = []
        for feature in feature_names:
            token_found = False
            for token in tokenized_question:
                if token == feature:
                    token_found = True
                    one_coded_list.append(1)
                    break
            if token_found == False:
                one_coded_list.append(0)

        question_array = np.array(one_coded_list)
        question_array = question_array.reshape((-1, 1))

        tfidf = tf.to_numpy()
        dot_result = np.dot(tfidf, question_array)
        max_index = dot_result.argmax(axis=0)
        max_index = max_index[0]
        return paragraphs[max_index]

    def get_answer(self, dataset, question):
        """Returns answer(s) for given question, context.
        Args:
            question: question of interest.
            context: context where appropriate answer can be found.
        Returns:
            A dictionary containing answer and other informations.
        """
        # 가장 score 가 높은 paragraph
        context = self.tfidf(dataset, question)
        # print(context)
        inputs = self.tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
        input_ids = inputs["input_ids"].tolist()[0]

        answer_start_scores, answer_end_scores = self.model(**inputs)

        answer_start = torch.argmax(answer_start_scores)
        answer_end = torch.argmax(answer_end_scores) + 1
        answer = self.tokenizer.convert_tokens_to_string(
            self.tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
        answer = remove_white_space(answer)

        return answer, context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name_or_path",
        default=None,
        type=str,
        required=True
    )
    parser.add_argument(
        "--data_path",
        default=None,
        type=str,
        required=True
    )

    args = parser.parse_args()
    with open(args.data_path, "r", encoding="utf-8") as reader:
        contexts = json.load(reader)["data"]

    # qa 객체 선언
    qa = Tfidf_QA_Module(args.model_name_or_path)

    # get_answer 함수를 호출하면 tf-idf 모듈을 통해 적합한 paragraph 를 찾고
    # QA 를 통한 결과(answer)를 반환해줌.
    predicted_answer = qa.get_answer(dataset=contexts, question="전략은 무엇인가요?")
    print(predicted_answer)


if __name__ == "__main__":
    main()
