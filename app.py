from pydantic import BaseModel, Field
from transformers import pipeline

from opyrator.components import outputs

MODEL_NAME = "songhee/i-manual-mbert"
mbert = pipeline("question-answering", model=MODEL_NAME, tokenizer=MODEL_NAME)


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
            {
                "question": input.question,
                "context": input.context,
            },
            topk=1,
        )
    elif model_name == 'koelectra'.lower():
        results = mbert(
            {
                "question": input.question,
                "context": input.context,
            },
            topk=1,
        )

    results = [results]

    return outputs.ClassificationOutput(
        __root__=[
            outputs.ScoredLabel(
                label=result["answer"],
                score=result["score"],
            )
            for result in results
        ]
    )
