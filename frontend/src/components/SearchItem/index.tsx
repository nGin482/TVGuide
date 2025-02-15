import { useContext, useEffect, useState } from "react";
import { App, Button, Dropdown, Popconfirm, Table, Tag, Typography } from "antd";
import type { MenuProps, TableColumnsType } from "antd";
import { EditOutlined, DeleteFilled } from "@ant-design/icons";

import { SearchItemForm } from "./SearchItemForm";
import { EmptyTableView } from "../EmptyTableView";
import { useShow } from "../../hooks/useShow";
import { UserContext } from "../../contexts";
import { addSearchCriteria, deleteSearchCriteria, editSearchCriteria } from "../../requests";
import { sessionExpiryMessage } from "../../utils";
import type { ErrorResponse, FormMode, SearchItem, SearchItemPayload } from "../../utils/types";
import "./SearchItem.css";


interface SearchItemProps {
    searchItem: SearchItem
    show: string
}

const SearchItem = ({ searchItem, show }: SearchItemProps) => {
    const [openModal, setOpenModal] = useState(false);
    const [formMode, setFormMode] = useState<FormMode>(null);

    const { updateShowContext } = useShow();
    const { currentUser } = useContext(UserContext);

    const { notification } = App.useApp();
    const { Text } = Typography;

    const addSearchItem = async (searchCriteria: SearchItemPayload) => {
        const newSearchItem = await addSearchCriteria(searchCriteria, currentUser.token);
        updateShowContext(show, "search_item", newSearchItem);
        return `The search criteria for ${show} has been added`;
    };

    const editSearchItem = async (searchCriteria: SearchItemPayload) => {
        const updatedSearchItem = await editSearchCriteria(searchCriteria, currentUser.token);
        updateShowContext(show, "search_item", updatedSearchItem);
        return `The search criteria for ${show} has been updated`;
    };

    const deleteSearchItemHandle = async () => {
        try {
            await deleteSearchCriteria(show, currentUser.token);
            updateShowContext(show, "search_item", null);
            notification.success({
                message: "Success!",
                description: `The reminder for ${show} has been deleted`,
                duration: 8
            });
        }
        catch(error) {
            let message: string =  error?.message;
            if (error?.response) {
                const responseError: ErrorResponse = error.response;
                if (responseError.data.msg) {
                    message = sessionExpiryMessage("delete this search criteria");
                }
                else {
                    message = responseError.data.message;
                }
            }
            notification.error({
                message: `Unable to delete the search criteria for ${show}`,
                description: message,
                duration: 8
            });
        }
    };

    const columns: TableColumnsType<SearchItem> = [
        {
            key: "search_active",
            dataIndex: "search_active",
            title: "Search Active",
            render: (search: boolean) => (
                <Tag color={search ? "green" : "red"}>
                    {search ? "Active" : "Inactive"}
                </Tag>
            )
        },
        {
            key: "exact_title_match",
            dataIndex: "exact_title_match",
            title: "Exact Title Match",
            render: (exact_title_match: boolean) => exact_title_match ? "Exact Match" : "Any matches"
        },
        {
            key: "min_season_number",
            dataIndex: ["conditions", "min_season_number"],
            title: "Min Season Number",
            render: (min_season_number: number) => min_season_number
        },
        {
            key: "max_season_number",
            dataIndex: ["conditions", "max_season_number"],
            title: "Max Season Number",
            render: (max_season_number: number) => max_season_number
        },
        {
            key: "ignore_episodes",
            dataIndex: ["conditions", "ignore_episodes"],
            title: "Ignore Episodes",
            render: (ignore_episodes: string[]) => (
                <ul>
                    {ignore_episodes.map(episode => (
                        <li key={episode}>{episode}</li>
                    ))}
                </ul>
            )
        },
        {
            key: "ignore_seasons",
            dataIndex: ["conditions", "ignore_seasons"],
            title: "Ignore Seasons",
            render: (ignore_seasons: number[]) => (
                <ul>
                    {ignore_seasons.map(season => (
                        <li key={season}>Season {season}</li>
                    ))}
                </ul>
            )
        },
        {
            key: "ignore_titles",
            dataIndex: ["conditions", "ignore_titles"],
            title: "Ignore Titles",
            render: (ignore_titles: string[]) => ignore_titles
        },
        {
            key: "actions",
            title: "Actions",
            render: () => (
                <Dropdown menu={{ items: menuItems }} trigger={["click"]}>
                    <Button>Edit {show} Search</Button>
                </Dropdown>
            )
        },
    ];

    const menuItems: MenuProps['items'] = [
        {
            icon: <EditOutlined />,
            key: "edit",
            label: "Edit",
            onClick: () => openForm("edit")
        },
        {
            key: "delete",
            label: (
                <Popconfirm
                    title={`Delete Search Criteria for ${show}?`}
                    okText="Delete"
                    okButtonProps={{ style: { background: "#f00" } } }
                    onConfirm={deleteSearchItemHandle}
                    onCancel={() => console.log("not deleted")}
                >
                    <DeleteFilled /> Delete
                </Popconfirm>
            ),
        }
    ];

    const openForm = (mode: FormMode) => {
        setFormMode(mode);
        setOpenModal(true);
    };

    const closeModal = () => {
        setOpenModal(false);
    };

    const EmptyDescription = () => (
        <>
            <Text type="secondary">No search item configured for {show}</Text>
            <br />
            <Button onClick={() => openForm("add")}>Add Search Criteria</Button>
        </>
    );

    return (
        <>
            <Table
                columns={currentUser ? columns : columns.filter(col => col.key !== "actions")}
                dataSource={searchItem ? [searchItem] : null}
                bordered
                locale={{
                    emptyText: <EmptyTableView description={<EmptyDescription />} />
                }}
                rowKey={record => record.show}
            />
            {openModal && (
                <SearchItemForm
                    mode={formMode}
                    open={openModal}
                    closeModal={closeModal}
                    successHandler={formMode === "add" ? addSearchItem : editSearchItem}
                    show={show}
                    searchItem={formMode === "edit" && searchItem}
                />
            )}
        </>
    );
};

export { SearchItem };