import { useContext, useState } from "react";
import { useHistory } from "react-router-dom";
import { Helmet } from "react-helmet";
import { Button, Card, Image } from "antd";

import AddShow from "../components/AddShow";
import { SearchItemTag } from "../components/SearchItemTag";
import { ShowsContext, UserContext } from "../contexts";
import { getSeasons } from "../utils";
import './styles/ShowsPage.css';

const ShowsPage = () => {
    const [addingNewShow, setAddingNewShow] = useState(false);

    const history = useHistory();
    const { shows } = useContext(ShowsContext);
    const { currentUser } = useContext(UserContext);

    return (
        <div id="recorded-shows-page">
            <Helmet>
                <title>Shows | TVGuide</title>
            </Helmet>
            <h1>List of Shows Recorded</h1>
            <p>Browse this page to view the episodes recorded for each show.</p>
            <div className="actions">
                {addingNewShow ? (
                    <AddShow
                        openModal={addingNewShow}
                        setOpenModal={setAddingNewShow}
                    />
                ) : (
                    currentUser && <Button onClick={() => setAddingNewShow(true)}>Add Show</Button>
                )}
            </div>
            <div id="shows-list">
                {shows.length > 0 && shows.map(show => (
                    <Card
                        key={show.show_name}
                        className="show"
                        onClick={() => history.push(`/shows/${show.show_name}`)}
                        title={(
                            <div className="card-title">
                                <span>{show.show_name}</span>
                                <SearchItemTag searchItem={show.search_item} />
                            </div>
                        )}
                        cover={<Image src={show.show_details.image} />}
                    >
                        <blockquote>
                            {`${getSeasons(show.show_episodes).length} `}
                            season{show.show_episodes.length > 1 && 's'}
                        </blockquote>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export { ShowsPage };