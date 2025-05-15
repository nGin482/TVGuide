import { useEffect, useState } from "react";
import { Alert, DatePicker, Spin, Table, TableColumnsType, Tag, Typography } from "antd";
import dayjs, { Dayjs } from "dayjs";

import { Guide, GuideShow, User } from "../../utils/types";
import { EmptyTableView } from "../EmptyTableView";
import { getGuide } from "../../requests/guide";
import './TVGuide.css';

const TVGuide = ({ user }: { user?: User }) => {
    const [date, setDate] = useState("");
    const [guide, setGuide] = useState<Guide>(null);
    const [guideShows, setGuideShows] = useState([]);
    const [loadingGuide, setLoadingGuide] = useState(false);
    const [error, setError] = useState("");

    const { Title } = Typography;

    useEffect(() => {
        setDate(dayjs().format("DD MMMM YYYY"));
        setLoadingGuide(true);
        fetchGuide();
    }, []);

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
        
        guideShows.sort((a, b) => sortShows(a, b));
        setGuideShows(guideShows);
    }, [guide, user]);

    const fetchGuide = async (date?: string) => {
        try {
            const guide = await getGuide(date);
            setGuide(guide);
            setError("");
        }
        catch(error) {
            if (error.response?.data.message) {
                setError(error.response.data.message);
            }
            else {
                setError('There is a problem communicating with the server');
            }
        }
        finally {
            setLoadingGuide(false);
        }
    };

    const sortShows = (a: GuideShow, b: GuideShow) => {
        if (a.start_time > b.start_time) {
            return 1;
        }
        if (a.start_time < b.start_time) {
            return -1;
        }
        return 0;
    };

    const handleDateChange = async (date: Dayjs) => {
        setGuide(null);
        setLoadingGuide(true);
        if (date) {
            setDate(date.format("DD MMMM YYYY"));
            await fetchGuide(date.format("DD/MM/YYYY"));
        }
        else {
            setDate(dayjs().format("DD MMMM YYYY"));
            await fetchGuide();
        }
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
            <div id="date">
                <Title level={5} className="date-selected">Date: {date}</Title>
                <DatePicker
                    onChange={handleDateChange}
                />
            </div>
            {loadingGuide && (
                <Spin size="large" />
            )}
            {guide && !loadingGuide && (
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
            )}
            {error && (
                <Alert
                    type="error"
                    message={(
                        <Title level={5}>There was a problem fetching the guide for {date}</Title>
                    )}
                    description={error}
                />
            )}
        </div>
    );
};

export default TVGuide;