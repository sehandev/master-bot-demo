import React from "react";

import { Container, Sidebar, Demo } from "@components";

const Home: React.FC = () => {
    return (
        <Container>
            <Sidebar model_name='mbert'>
                <Demo model_name='mbert' />
            </Sidebar>
        </Container>
    );
};

export default Home;
