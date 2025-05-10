import { useEffect, useState } from "react";
import { Table, TableColumnsType, Tag } from "antd";

import { Guide, GuideShow, User } from "../../utils/types";
import { EmptyTableView } from "../EmptyTableView";
import { getGuide } from "../../requests/guide";
import './TVGuide.css';

const TVGuide = ({ user }: { user?: User }) => {
    const [guide, setGuide] = useState<Guide>(null);
    const [guideShows, setGuideShows] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchGuide();
    }, []);

    const fetchGuide = async () => {
        try {
            const guide = await getGuide();
            console.log(guide)
            setGuide(guide);
        }
        catch(error) {
            if (error.response?.data.message) {
                setError(error.response.data.message);
            }
            else {
                setError('There is a problem communicating with the server');
            }
        }
    };

    useEffect(() => {
        let guideShows: GuideShow[] = guide ? guide.fta : [];

        if (user) {
            const userSubscriptions = user.show_subscriptions.map(
                subscription => subscription.search_item.show
            );
            guideShows = guideShows.filter(
                guideEpisode => userSubscriptions.includes(guideEpisode.title)
            );
        }
        
        guideShows.sort((a, b) => sortServices(a, b));
        setGuideShows(guideShows);
    }, [guide, user]);

    const sortServices = (a: GuideShow, b: GuideShow) => {
        if (a.start_time > b.start_time) {
            return 1;
        }
        if (a.start_time < b.start_time) {
            return -1;
        }
        return 0;
    };

    const tableColumns: TableColumnsType<GuideShow> = [
        {
            title: 'Show',
            dataIndex: 'title',
            key: 'show'
        },
        {
            title: 'Start Time',
            dataIndex: 'start_time',
            key: 'start_time'
        },
        {
            title: 'End Time',
            dataIndex: 'end_time',
            key: 'end_time'
        },
        {
            title: 'Channel',
            dataIndex: 'channel',
            key: 'channel'
        },
        {
            title: 'Season Number',
            dataIndex: 'season_number',
            key: 'season_number'
        },
        {
            title: 'Episode Number',
            dataIndex: 'episode_number',
            key: 'episode_number'
        },
        {
            title: 'Episode Title',
            dataIndex: 'episode_title',
            key: 'episode_title'
        },
        {
            title: 'Repeat?',
            dataIndex: 'repeat',
            key: 'repeat',
            render: (repeat: boolean) => repeat && <Tag color="orange">Repeat</Tag>
        }
    ];

    return (
        <div id="tv-guide">
            <Table
                className="guide-table"
                columns={tableColumns}
                dataSource={guideShows}
                bordered={true}
                pagination={
                    {
                        position: ['bottomCenter'],
                        pageSize: 50,
                        hideOnSinglePage: true,
                    }
                }
                locale={{
                    emptyText: <EmptyTableView description="No episodes for this day" />,
                }}
                rowKey={record => `${record.channel}-${record.start_time}`}
            />
        </div>
    );
};

export default TVGuide;