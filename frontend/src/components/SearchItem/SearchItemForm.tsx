import { useContext, useEffect, useState } from "react";
import { App, Checkbox, Form, Modal, Radio, Select, Space, Spin } from "antd";

import { ShowsContext } from "../../contexts";
import { getEpisodes, getShowSeasons } from "../../requests";
import { createSearchItemPayload, sessionExpiryMessage } from "../../utils";
import {
    ErrorResponse,
    SearchItem,
    SearchItemFormValues,
    SearchItemPayload,
    ShowData,
    TVMazeSeason
} from "../../utils/types";
import { TVMazeEpisode } from "../../utils/types/tvmaze";


interface AddSearchItemProps {
    mode: "add" | "edit"
    open: boolean
    show: string
    closeModal: () => void
    successHandler: (searchCriteria: SearchItemPayload) => Promise<string>
    searchItem?: SearchItem
}

interface FormValues {
    exactSearch: boolean
    seasonChoice: "all" | "some"
    seasons: number[]
    ignoreEpisodes: string[]
}

const SearchItemForm = (props: AddSearchItemProps) => {
    const { mode, open, closeModal, successHandler, show, searchItem } = props;

    const [showData, setShowData] = useState<ShowData>();
    const [showSeasons, setShowSeasons] = useState<TVMazeSeason[]>(null);
    const [formValues, setFormValues] = useState<FormValues>(null);
    const [showEpisodes, setShowEpisodes] = useState<TVMazeEpisode[]>(null);
    const [filteredEpisodes, setFilteredEpisodes] = useState<TVMazeEpisode[]>(null);

    const { shows } = useContext(ShowsContext);
    const { notification } = App.useApp();

    const [form] = Form.useForm<SearchItemFormValues>();

    useEffect(() => {
        const showItem = shows.find(showData => showData.show_name === show);
        setShowData(showItem)
    }, []);

    useEffect(() => {
        if (showData) {
            const tvmazeId = showData.show_details.tvmaze_id;
            fetchShowSeasons(tvmazeId);
            fetchShowEpisodes(tvmazeId);
        }
    }, [showData]);
    
    useEffect(() => {
        if (showSeasons) {
            setInitialValuesForSeasons();
        }
    }, [showSeasons]);

    useEffect(() => {
        console.log(formValues)
    }, [formValues]);


    const handleFormUpdate = (field: keyof FormValues, value: string | string[] | number[]) => {
        setFormValues(current => ({ ...current, [field]: value }));
        if (field === "seasonChoice" && value === "all") {
            setFormValues(current => ({ ...current, seasons: [] }));
        }
    };

    const filterOptions = (input: string) => {
        setFilteredEpisodes(showEpisodes.filter(
            episode => episode.name.toLowerCase().includes(input.toLowerCase())
        ));
    };

    const createEpisodeLabel = (episode: TVMazeEpisode) => {
        return `Season ${episode.season} Episode ${episode.number}: ${episode.name}`;
    };

    const fetchShowSeasons = async (tvmazeId: string) => {
        const seasons = await getShowSeasons(tvmazeId);
        setShowSeasons(seasons);
    };
    
    const fetchShowEpisodes = async (tvmazeId: string) => {
        const episodes = await getEpisodes(tvmazeId);
        setShowEpisodes(episodes);
        setFilteredEpisodes(episodes);
    };

    const setInitialValuesForSeasons = () => {
        if (searchItem.conditions && searchItem.conditions?.ignore_seasons.length !== 0) {
            const seasonsSelected = showSeasons.filter(
                season => !searchItem.conditions?.ignore_seasons.includes(season.number)
            );
            form.setFields([
                {
                    name: "seasonChoice",
                    value: "some"
                },
                {
                    name: "seasons",
                    value: seasonsSelected.map(season => season.number)
                }
            ]);
            handleFormUpdate("seasonChoice", "some");
            handleFormUpdate("seasons", seasonsSelected.map(season => season.number));
        }
        else {
            form.setFields([
                {
                    name: "seasonChoice",
                    value: "all"
                },
                {
                    name: "seasons",
                    value: null
                }
            ]);
            handleFormUpdate("seasons", []);
            handleFormUpdate("seasonChoice", "all");
        }
    }

    const submitSearchItem = async () => {
        form.validateFields();
        if (!form.getFieldsValue().exactSearch) {
            form.setFieldValue("exactSearch", false);
        }
        
        const formValues = form.getFieldsValue();

        const searchConditions = createSearchItemPayload(show, formValues,  showSeasons);

        const searchItem: SearchItemPayload = {
            show: show,
            conditions: searchConditions
        };

        try {
            const result = await successHandler(searchItem);
            notification.success({
                message: 'Success!',
                description: result,
                duration: 8
            });
            closeModal();
        }
        catch(error) {
            let message: string =  error?.message;
            if (error?.response) {
                const responseError: ErrorResponse = error.response;
                if (responseError.data.msg) {
                    message = sessionExpiryMessage("add this search criteria");
                }
                else {
                    message = responseError.data.message;
                }
            }
            notification.error({
                message: `Unable to add the search criteria for ${show}`,
                description: message,
                duration: 8
            });
        }
    };

    return (
        showData ? (
            <Modal
                open={open}
                title={`${mode[0].toUpperCase() + mode.slice(1)} Search Criteria for ${showData.show_name}`}
                onCancel={closeModal}
                onOk={submitSearchItem}
            >
                <Form
                    form={form}
                >
                    <Form.Item
                        name="exactSearch"
                        valuePropName="checked"
                        initialValue={searchItem.exact_title_match}
                    >
                        <Checkbox name="exact_search">Exact Title Match</Checkbox>
                    </Form.Item>
                    <Form.Item
                            name="seasonChoice"
                            label="How many seasons?"
                            required
                            rules={[
                                {
                                    required: true,
                                    message: "Please select how many seasons you'd like"
                                }
                            ]}
                        >
                            <Radio.Group
                                onChange={value => handleFormUpdate(
                                    "seasonChoice",
                                    value.target.value)
                                }
                            >
                                <Space direction="vertical">
                                    <Radio value="all">All Seasons</Radio>
                                    <Radio value="some">Some Seasons</Radio>
                                </Space>
                            </Radio.Group>
                        </Form.Item>
                    {formValues?.seasonChoice === "some" && (
                        <Form.Item
                            name="seasons"
                            label="Seasons"
                        >
                            <Select
                                options={showSeasons ? showSeasons.map(season => (
                                    {
                                        label: `Season ${season.number}`,
                                        value: season.number
                                    }
                                )) : []}
                                mode="multiple"
                                onChange={(value: number[]) => handleFormUpdate("seasons", value)}
                                allowClear
                            />
                        </Form.Item>
                    )}
                    <Form.Item
                            name="ignoreEpisodes"
                            label="Ignore Episodes"
                            initialValue={searchItem?.conditions?.ignore_episodes}
                        >
                            <Select
                                options={filteredEpisodes ? filteredEpisodes.map(episode => (
                                    {
                                        label: createEpisodeLabel(episode),
                                        value: episode.name
                                    }
                                )) : []}
                                onSearch={value => filterOptions(value)}
                                onChange={(value: string[]) => handleFormUpdate(
                                    "ignoreEpisodes",
                                    value
                                )}
                                mode="multiple"
                                allowClear
                            />
                        </Form.Item>
                </Form>
            </Modal>
        ) : (
            <Spin fullscreen />
        )
    );
};

export { SearchItemForm };