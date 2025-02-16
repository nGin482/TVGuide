import { useContext, useState } from 'react';
import { Helmet } from 'react-helmet';
import {
    App,
    Alert,
    Button,
    Dropdown,
    Popconfirm,
    Table,
    TableColumnsType,
    Tag,
    Typography
} from 'antd';
import { DeleteFilled, EditOutlined } from "@ant-design/icons";
import type { MenuProps } from 'antd';
import dayjs from 'dayjs';

import { EmptyTableView } from '../EmptyTableView';
import { EpisodeForm } from './EpisodeForm';
import { UserContext } from '../../contexts';
import { useShow } from '../../hooks/useShow';
import { updateShowEpisode } from '../../requests';
import { getSeasons, sessionExpiryMessage } from '../../utils';
import { ShowEpisode } from '../../utils/types';
import "./ShowEpisode.css";

interface ShowProps {
    episodes: ShowEpisode[]
    showName: string
};

const ShowEpisodes = ({ episodes, showName }: ShowProps) => {
    const [season, setSeason] = useState(1);
    const [episodeEdited, setEpisodeEdited] = useState<ShowEpisode>(null);
    const [showForm, setShowForm] = useState(false);

    const { notification } = App.useApp();
    const { currentUser } = useContext(UserContext);
    const { updateEpisodeContext } = useShow();

    const { Text } = Typography;

    const toggleForm = () => {
        setShowForm(current => !current);
    };

    const updateEpisode = async (formValues: ShowEpisode) => {
        try {
            const updatedEpisode = await updateShowEpisode(formValues, currentUser.token);
            updateEpisodeContext(formValues.show, formValues.id, updatedEpisode);
            notification.success({
                message: "Success!",
                description: `The episode '${formValues.episode_title}' has been updated`,
                duration: 8
            });
            toggleForm();
            setEpisodeEdited(null);
        }
        catch(error) {
            let message: string =  error?.message;
            if (error?.response) {
                if (error.response?.data.msg) {
                    message = sessionExpiryMessage("update this episode");
                }
                else {
                    message = error.response.data.message;
                }
            }
            notification.error({
                message: `Unable to edit the episode for '${formValues.episode_title}'`,
                description: message,
                duration: 8
            });
        }
    };

    const deleteEpisodeHandle = () => {
        console.log(`deleting episode ${episodeEdited.episode_title} with id ${episodeEdited.id}`)
    };

    const episodeColumns: TableColumnsType<ShowEpisode> = [
        {
            key: 'season_number',
            dataIndex: 'season_number',
            title: 'Season Number'
        },
        {
            key: 'episode_number',
            dataIndex: 'episode_number',
            title: 'Episode Number'
        },
        {
            key: 'episode_title',
            dataIndex: 'episode_title',
            title: 'Episode Title'
        },
        {
            key: 'alternative_titles',
            dataIndex: 'alternative_titles',
            title: 'Alternative Titles'
        },
        {
            key: 'summary',
            dataIndex: 'summary',
            title: 'Summary',
            render: (summary: string) => <div dangerouslySetInnerHTML={{__html: summary}} />
        },
        {
            key: 'channels',
            dataIndex: 'channels',
            className: 'episode-channels',
            title: 'Channels',
            render: (channels: string[]) => channels.map((channel, index) =>
                <Tag
                    key={`tag-${index}-${channel}`}
                    color="geekblue"
                    className="episode-channel"
                >
                    {channel}
                </Tag>
            )
        },
        {
            key: 'air_dates',
            dataIndex: 'air_dates',
            className: 'episode-air-dates',
            title: 'Air Dates',
            render: (air_dates: Date[]) => air_dates.map((air_date, index) =>
                <Tag
                    key={`tag-${index}-${air_date}`}
                    color="geekblue"
                    className="episode-channel"
                >
                    {dayjs(air_date).format("DD/MM/YYYY")}
                </Tag>
            )
        },
        {
            key: "actions",
            className: "actions",
            title: "Actions",
            render: (record: ShowEpisode) => (
                <Dropdown
                    menu={{ items: menuItems }}
                    trigger={["click"]}
                    onOpenChange={() => setEpisodeEdited(record)}
                >
                    <Button>Edit Episode</Button>
                </Dropdown>
            )
        },
    ];

    const menuItems: MenuProps['items'] = [
        {
            icon: <EditOutlined />,
            key: "edit",
            label: "Edit",
            onClick: toggleForm
        },
        {
            key: "delete",
            label: (
                <Popconfirm
                    title={`Delete Episode?`}
                    okText="Delete"
                    okButtonProps={{ style: { background: "#f00" } } }
                    onConfirm={deleteEpisodeHandle}
                    onCancel={() => console.log("not deleted")}
                >
                    <DeleteFilled /> Delete
                </Popconfirm>
            ),
        }
    ];

    const EmptyDescription = () => (
        <>
            <Text>No episodes found for {showName}</Text>
            <br />
            <Button>Get Episodes</Button>
        </>
    );

    return (
        episodes ? (
            <div className="episodes">
                <Helmet>
                    <title>{showName} Episodes | TVGuide</title>
                </Helmet>

                <h3>Episodes</h3>
                {getSeasons(episodes).map(seasonNumber => 
                    <Button
                        className={seasonNumber === season ? "change-season-active" : "change-season" }
                        onClick={() => setSeason(seasonNumber)}
                        key={seasonNumber}
                        data-testid={`season-${seasonNumber}`}
                    >
                        Season {seasonNumber === -1 ? "Unknown" : seasonNumber}
                    </Button>
                )}
                <Table
                    data-testid={`${showName}-table`}
                    key={`${showName}-table`}
                    rowKey={record => record.episode_title}
                    columns={episodeColumns}
                    dataSource={episodes.filter(episode => episode.season_number === season)}
                    className='season-table'
                    bordered={true}
                    pagination={
                        {
                            position: ['bottomCenter'],
                            pageSize: 50,
                            hideOnSinglePage: true
                        }
                    }
                    locale={{
                        emptyText: <EmptyTableView description={<EmptyDescription />} />
                    }}
                />
                {showForm && (
                    <EpisodeForm
                        showName={showName}
                        episodeId={episodeEdited.id}
                        open={showForm}
                        closeForm={toggleForm}
                        updateHandler={updateEpisode}
                    />
                )}
            </div>
        )
        : (
            <>
                <Alert type="error" message="A problem occurred retrieving the episodes for this show" />
            </>
        )
    );    
};


export { ShowEpisodes };