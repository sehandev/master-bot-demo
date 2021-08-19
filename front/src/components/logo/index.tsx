import React from "react";
import Image from "next/image";

export const Logo: React.FC = () => {
    return (
        <Image
            src="/images/2b3e-logo.png"
            alt="2b3e logo"
            width="40"
            height="40"
        />
    );
};
