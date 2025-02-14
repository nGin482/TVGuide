import { Image, List } from "antd";

import type { ShowDetails } from "../../utils/types";
import "./ShowDetails.css";


interface ShowDetailsProps {
    showDetails: ShowDetails
}

const ShowDetails = ({ showDetails }: ShowDetailsProps) => (
    <>
        <div style={{ display: "flex", justifyContent: "space-evenly" }}>
            <Image src={showDetails.image} width="auto" height={500} />
            <List
                dataSource={showDetails.genres}
                renderItem={item => (
                    <List.Item>
                        {item}
                    </List.Item>
                )}
                bordered
                header={<h1>Genres</h1>}
                className="genres-list"
            />
        </div>
        <div
            dangerouslySetInnerHTML={{ __html: showDetails.description }}
            className="show-description"
        />
    </>
);

export { ShowDetails };