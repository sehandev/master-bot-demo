import React, { useState } from "react";
import Image from 'next/image'
import Link from 'next/link'

import { Logo } from "@components";
import data from "@public/mbert.json";

type Props = {
    children: React.ReactNode
    model_name: string
}

export const Sidebar: React.FC<Props> = ({ children, model_name }) => {
    const titles = Object.keys(data)
    const [model, set_model] = useState(model_name)

    const change_model = () => {
        if (model == 'mbert') {
            set_model('koelectra')
        }
        else {
            set_model('mbert')
        }
    }

    return (
        <div className="flex mb-12 w-full min-h-screen">
            <div className="p-4 rounded-br-xl shadow" style={{ minWidth: '16rem', backgroundColor: '#e0dcd3' }}>
                <Link href={'/'}>
                    <div className="flex items-center space-x-4 pl-4 py-2 mb-5 rounded-full cursor-pointer">
                        <Logo />
                        <div>
                            <h1 className="font-bold">Masterbot Demo</h1>
                            <span className="text-sm text-gray-600">&copy; 2B3E sehandev</span>
                        </div>
                    </div>
                </Link>

                <div className="flex items-center justify-center mb-4">
                    <label
                        htmlFor="toogleA"
                        className="flex items-center cursor-pointer"
                        onClick={change_model}
                    >
                        <div className="text-gray-700 text-xs font-bold">
                            mBERT
                        </div>
                        <div className="relative mx-3">
                            <input type="checkbox" className="sr-only" checked={model == 'koelectra'} />
                            <div className="w-10 h-4 bg-gray-400 rounded-full shadow-inner" />
                            <div className="dot absolute w-6 h-6 rounded-full shadow -left-1 -top-1 transition" />
                        </div>
                        <div className="text-gray-700 text-xs font-bold">
                            KoELECTRA
                        </div>
                    </label>

                </div>

                <ul className="space-y-2 text-sm">
                    {titles.map((title) => {
                        return (
                            <li key={title}>
                                <Link href={`/${model}/${encodeURIComponent(title)}`}>
                                    <a className="flex space-x-3 p-2 rounded-md hover:bg-gray-100 focus:bg-gray-100 text-gray-700 hover:text-gray-900 font-bold">
                                        <Image
                                            src="/icons/message.svg"
                                            alt="message"
                                            width="18px"
                                            height="18px"
                                        />
                                        <span>{title}</span>
                                    </a>
                                </Link>
                            </li>
                        )
                    })}
                </ul>
            </div>

            <div className="w-full p-8">
                {children}
            </div>
        </div>
    );
};
