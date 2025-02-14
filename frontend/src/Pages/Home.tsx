import { useState, useEffect } from "react";
import { Helmet } from "react-helmet";

import TVGuide from "../components/TVGuide";
import { getGuide } from "../requests";
import { Guide } from "../utils/types";

const Home = () => {
    const [guide, setGuide] = useState<Guide | null>(null);
    const [guideError, setGuideError] = useState<string>('');

    useEffect(() => {
        fetchGuide()
    }, []);

    const fetchGuide = async () => {
        try {
            const guide = await getGuide();
            setGuide(guide);
        }
        catch(error) {
            if (error.response?.data.message) {
                setGuideError(error.response.data.message);
            }
            else {
                setGuideError('There is a problem communicating with the server');
            }
        }
    };

    return (
        <div id="home">
            <Helmet>
                <title>Home | TVGuide</title>
            </Helmet>
            <h1>TV Guide</h1>
            {guide ? <TVGuide guide={guide} /> : <blockquote id="message">{guideError}</blockquote>}
        </div>
    );
};

export default Home;