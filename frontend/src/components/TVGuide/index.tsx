import { useEffect, useState } from "react";
import { Table, TableColumnsType, Tag } from "antd";
import dayjs, { Dayjs } from "dayjs";
import isBetween from "dayjs/plugin/isBetween";
import Timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";

import { Guide, GuideShow, User } from "../../utils/types";
import { EmptyTableView } from "../EmptyTableView";
import './TVGuide.css';

dayjs.extend(isBetween);
dayjs.extend(utc);
dayjs.extend(Timezone);

const TVGuide = ({ guide, user }: { guide: Guide, user?: User }) => {
    const [guideShows, setGuideShows] = useState([]);
    const [currentTime, setCurrentTime] = useState<Dayjs>(dayjs());

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(dayjs().tz("Australia/Sydney"));
        }, 60000);
        return () => clearInterval(interval);
    }, []);

    const isShowAiring = (episode: GuideShow) => {
        const startTime = dayjs(episode.start_time, "HH:mm");
        const endTime = dayjs(episode.end_time, "HH:mm");
        if (currentTime.isBetween(startTime, endTime, null, "[]")) {
            return "airing";
        }
        else if (currentTime.isAfter(endTime)) {
            return "finished";
        }
    };

    useEffect(() => {
        let guideShows = guide?.fta || [];

        if (user) {
            const userSubscriptions = user.show_subscriptions.map(
                subscription => subscription.search_item.show
            );
            guideShows = guideShows.filter(
                guideEpisode => userSubscriptions.includes(guideEpisode.title)
            );
        }
        
        guideShows.sort((a, b) => sortShows(a, b));
        setGuideShows(guideShows);
    }, [guide, user]);

    const sortShows = (a: GuideShow, b: GuideShow) => {
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
                rowClassName={(record) => isShowAiring(record)}
            />
        </div>
    );
};

export default TVGuide;