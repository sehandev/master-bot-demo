import React from "react";

import { Container, Sidebar, Demo } from "@components";

const Home: React.FC = () => {
    return (
        <Container>
            <Sidebar model_name='koelectra'>
                <Demo model_name='koelectra' />
            </Sidebar>
        </Container>
    );
};

export default Home;
