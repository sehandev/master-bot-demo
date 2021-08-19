import React, { useEffect, useState } from "react"
import { useRouter } from 'next/router'
import axios, { AxiosResponse } from 'axios'

import mbert_data from "@public/mbert.json";
import koelectra_data from "@public/koelectra.json";

interface QnA {
    question: string
    answer: string
}

interface Content {
    context: string
    qas: QnA[]
}

interface Dict {
    [key: string]: Content[]
}

type Props = {
    model_name: string
}


export const Demo: React.FC<Props> = ({ model_name }) => {
    const router = useRouter()
    const query = router.query
    const decoded_title = decodeURIComponent(query.title as string)
    const data: Dict = model_name == 'mbert' ? mbert_data : koelectra_data
    const contents = data[decoded_title]

    const [context_idx, set_context_idx] = useState(0)
    const [context, set_context] = useState('')
    const [new_question, set_new_question] = useState('')

    const [qa_array, set_qa_array] = useState<QnA[]>([])

    useEffect(() => {
        set_context_idx(0)

        if (contents) {
            set_context(contents[context_idx].context)
            set_qa_array(contents[context_idx].qas)
        }
    }, [decoded_title])

    const post_qa = (question: string) => {
        const json = JSON.stringify({
            model_name: "mbert",
            context: context,
            question: question,
        })

        axios.post('http://223.194.70.78:8125/call', json, {
            headers: {
                'Content-Type': 'application/json'
            },
        }).then((response: AxiosResponse) => {
            const answer = response.data[0].label
            console.log('answer', answer)
            set_qa_array(oldArray => [...oldArray, { question: question, answer: answer }])
        }).catch(function (error) {
            console.log(error)
        })

        set_new_question('')
    }

    const ContextNav = () => {
        return (
            <>
                <nav className="bg-gray-100 mb-4">
                    <div className="min-w-full px-2 sm:px-4 lg:px-6">
                        <div className="relative flex items-center py-2">
                            <div className="flex space-x-4">
                                <h2 className="mr-2 py-1 text-black">Context</h2>

                                {contents && contents.map((content, idx) => {
                                    return (
                                        <button
                                            key={idx}
                                            onClick={() => {
                                                set_context_idx(idx)
                                                set_context(content.context)
                                                set_qa_array(content.qas)
                                            }}
                                            className="text-gray-500 hover:bg-gray-200 hover:text-gray-900 px-3 py-1 rounded-md text-sm"
                                        >
                                            {idx + 1}
                                        </button>

                                    )
                                })}
                            </div>
                        </div>
                    </div>
                </nav>

                <p className="mb-6">
                    {context}
                </p>
            </>
        )
    }

    return (
        <div className="max-w-5xl">
            <ContextNav />

            <div className="flex flex-col">
                <div className="-ml-1">
                    <div className="px-1 w-full">
                        <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th scope="col" className="px-4 py-2 text-left text-sm text-gray-500">
                                            질문
                                        </th>
                                        <th scope="col" className="px-4 py-2 text-left text-sm text-gray-500">
                                            답변
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {qa_array.map((qa, idx) => {
                                        if (qa.answer) {
                                            return (
                                                <tr key={idx}>
                                                    <td className="w-1/3 px-4 py-4">
                                                        <div className="text-sm text-gray-900">{qa.question}</div>
                                                    </td>
                                                    <td className="w-2/3 px-4 py-4">
                                                        <div className="text-sm text-gray-900">{qa.answer}</div>
                                                    </td>
                                                </tr>
                                            )
                                        }
                                    })}

                                    {/* 실시간 QA */}
                                    <tr>
                                        <td className="w-1/3 px-4 py-4">
                                            <input
                                                type="text"
                                                value={new_question}
                                                onChange={(e) => set_new_question(e.target.value)}
                                                onKeyPress={(e) => {
                                                    if (e.key == 'Enter') {
                                                        post_qa(new_question)
                                                    }
                                                }}
                                                className="mr-2 px-2 py-2 border border-grey-700 rounded-md"
                                                placeholder="추가 질문"
                                            />
                                        </td>
                                        <td className="w-2/3 px-4 py-4">
                                            <button onClick={() => post_qa(new_question)} className="px-2 py-1 bg-gray-100 hover:bg-gray-200 border border-gray-300 text-sm">질문하기</button>
                                        </td>
                                    </tr>

                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
