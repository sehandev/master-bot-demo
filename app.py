# Standard
import json
from pathlib import Path

# PIP
from pydantic import BaseModel, Field
from opyrator.components import outputs

# Custom
from util import QuestionAnswering
from tfidf import Tfidf_QA_Module

PROJECT_DIR = Path(__file__).parent.absolute()

mbert = QuestionAnswering("songhee/i-manual-mbert")
koelectra = QuestionAnswering("mtr0930/koelectra-base-v3_epoch-100")
tfidf_module = Tfidf_QA_Module("mtr0930/i-manual_tokenizer_updated")

with open(PROJECT_DIR / "data/tfidf.json", "r", encoding="utf-8") as reader:
    tfidf_contexts = json.load(reader)["data"]


class QuestionAnsweringInput(BaseModel):
    model_name: str = Field(
        ...,
        description="finetuned model for korean qa - mbert, koelectra",
        example="mbert",
        max_length=100,
    )
    context: str = Field(
        ...,
        description="A string that contains the answer to the question.",
        example="My name is Sarah and I live in London",
        max_length=1000,
    )
    question: str = Field(
        ...,
        description="The question as a string that has an answer within context.",
        example="Where do I live?",
        max_length=140,
    )


def question_answering(input: QuestionAnsweringInput) -> outputs.ClassificationOutput:

    model_name = input.model_name.lower()
    if model_name == 'mbert'.lower():
        results = mbert(
            context=input.context,
            question=input.question,
        )
        context = input.context
        answer = results["answer"]
    elif model_name == 'koelectra'.lower():
        results = koelectra(
            context=input.context,
            question=input.question,
        )
        context = input.context
        answer = results["answer"]
    elif model_name == 'tfidf'.lower():
        answer, context = tfidf_module.get_answer(
            dataset=tfidf_contexts,
            question=input.question,
        )

    results = [answer, context]

    return outputs.ClassificationOutput(
        __root__=[
            outputs.ScoredLabel(
                label=result.replace('[UNK]', '...'),
                score=0,
            )
            for result in results
        ]
    )
