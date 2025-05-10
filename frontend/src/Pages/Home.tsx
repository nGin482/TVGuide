import { Helmet } from "react-helmet";

import TVGuide from "../components/TVGuide";

const Home = () => {
    
    return (
        <div id="home">
            <Helmet>
                <title>Home | TVGuide</title>
            </Helmet>
            <h1>TV Guide</h1>
            <TVGuide />
        </div>
    );
};

export default Home;