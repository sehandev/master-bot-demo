import React, { useEffect, useState } from "react"
import axios, { AxiosResponse } from 'axios'

import tfidf_data from "@public/tfidf.json";

interface QnA {
    question: string
    context: string
    answer: string
}

export const FullDemo: React.FC = () => {
    const [new_question, set_new_question] = useState('')
    const [qa_array, set_qa_array] = useState<QnA[]>([])

    useEffect(() => {
        if (tfidf_data) {
            let random_array = tfidf_data.sort(() => .5 - Math.random()).slice(0, 5)
            set_qa_array(random_array)
        }
    }, [])

    const post_qa = (question: string) => {
        const json = JSON.stringify({
            model_name: "tfidf",
            context: "",
            question: question,
        })

        axios.post('http://223.194.70.78:8126/call', json, {
            headers: {
                'Content-Type': 'application/json'
            },
        }).then((response: AxiosResponse) => {
            const answer = response.data[0].label
            const context = response.data[1].label
            set_qa_array(oldArray => [{ question: question, context: context, answer: answer }, ...oldArray])
        }).catch(function (error) {
            console.log(error)
        })

        set_new_question('')
    }

    return (
        <div className="mx-auto p-4">
            <div className="flex mb-4 text-lg font-bold text-center">마스터봇 전체 QA</div>

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
                                            지문
                                        </th>
                                        <th scope="col" className="px-4 py-2 text-left text-sm text-gray-500">
                                            답변
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">

                                    {/* 실시간 QA */}
                                    <tr>
                                        <td className="w-1/6 px-4 py-4">
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
                                        <td className="w-2/6 px-4 py-4"></td>
                                        <td className="w-2/6 px-4 py-4">
                                            <button onClick={() => post_qa(new_question)} className="px-2 py-1 bg-gray-100 hover:bg-gray-200 border border-gray-300 text-sm">질문하기</button>
                                        </td>
                                    </tr>
                                    {qa_array.map((qa, idx) => {
                                        return (
                                            <tr key={idx}>
                                                <td className="w-1/6 px-4 py-4">
                                                    <div className="text-sm text-gray-900">{qa.question}</div>
                                                </td>
                                                <td className="w-2/6 px-4 py-4">
                                                    <div className="text-sm text-gray-900">{qa.context}</div>
                                                </td>
                                                <td className="w-2/6 px-4 py-4">
                                                    <div className="text-sm text-gray-900">{qa.answer}</div>
                                                </td>
                                            </tr>
                                        )
                                    })}

                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
