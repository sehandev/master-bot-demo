from transformers import AutoTokenizer, AutoModelForQuestionAnswering, AutoConfig
import torch


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
    r_space = [",", ".", "!", "?", ")", "~", "%"]  # 이전 토큰에 붙어야하는 토큰
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    n_space = ["(", "/", "’"]  # 앞뒤 토큰 모두 붙어야 하는 토큰
    length = len(tokens)

    result = []
    result.append(tokens[0])
    l_s = False
    for i in range(1, length):

        # 앞 뒤로 다 붙어야 하는 경우
        if tokens[i] in n_space:
            result[-1] = result[-1] + tokens[i]
            l_s = True
            continue

        if (tokens[i-1] == "~" or tokens[i-1] == ".") and tokens[i][0] in numbers:
            result[-1] = result[-1] + tokens[i]
            continue

        if (tokens[i-1] == "'" and toggle) or (tokens[i-1] == ")" and len(tokens[i]) == 1):
            result[-1] = result[-1] + tokens[i]
            continue

        # 다음 토큰에 붙어야 하는 경우
        if tokens[i] in l_space or (tokens[i] == "'" and toggle):
            l_s = True

            result.append(tokens[i])

            if tokens[i] == "'":
                toggle = False

            continue

        # 앞 토큰에 붙어야 하는 경우
        if (tokens[i] in r_space) or l_s or (tokens[i] == "'" and toggle == False):
            result[-1] = result[-1] + tokens[i]
            l_s = False

            if tokens[i] == "'":
                toggle = True

            continue

        result.append(tokens[i])

    return " ".join(result)


class QuestionAnswering():
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
        self.model = AutoModelForQuestionAnswering.from_pretrained(
            pretrained_model_name_or_path,
            config=self.config)
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path)

        self.model = self.model.cuda()

    def __call__(self, question, context):
        """Returns answer(s) for given question, context.
        Args:
            question: question of interest.
            context: context where appropriate answer can be found.
        Returns:
            A dictionary containing answer and other informations.
        """

        inputs = self.tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
        inputs = inputs.to('cuda:0')
        input_ids = inputs["input_ids"].tolist()[0]

        text_tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
        answer_start_scores, answer_end_scores = self.model(**inputs, return_dict=False)

        answer_start = torch.argmax(answer_start_scores)  # Get the most likely beginning of answer with the argmax of the score
        answer_end = torch.argmax(answer_end_scores) + 1  # Get the most likely end of answer with the argmax of the score

        answer = self.tokenizer.convert_tokens_to_string(self.tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
        answer = remove_white_space(answer)

        return {
            "question": question,
            "answer": answer,
            "input_ids": input_ids,
            "text_tokens": text_tokens,
            "answer_start": answer_start,
            "answer_end": answer_end,
        }
