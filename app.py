from pydantic import BaseModel, Field
from transformers import pipeline
from opyrator.components import outputs

from util import QuestionAnswering

mbert = QuestionAnswering("songhee/i-manual-mbert")
koelectra = QuestionAnswering("mtr0930/koelectra-base-v3_epoch-100")


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
    elif model_name == 'koelectra'.lower():
        results = koelectra(
            context=input.context,
            question=input.question,
        )

    results = [results]

    return outputs.ClassificationOutput(
        __root__=[
            outputs.ScoredLabel(
                label=result["answer"].replace('[UNK]', '...'),
                score=0,
            )
            for result in results
        ]
    )
