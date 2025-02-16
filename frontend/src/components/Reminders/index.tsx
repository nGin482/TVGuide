import { useContext, useState } from "react";
import { App, Button, Dropdown, Popconfirm, Table, Typography } from "antd";
import { EditOutlined, DeleteFilled } from "@ant-design/icons";
import type { MenuProps, TableColumnsType } from "antd";

import { ReminderForm } from "./ReminderForm";
import { EmptyTableView } from "../EmptyTableView";
import { UserContext } from "../../contexts";
import { useShow } from "../../hooks/useShow";
import { addReminder, deleteReminder, editReminder } from "../../requests";
import { sessionExpiryMessage } from "../../utils";
import type { ErrorResponse, FormMode, Reminder, ReminderFormValues } from "../../utils/types";

interface ReminderProps {
    reminder: Reminder
    show?: string
}

const Reminder = ({ reminder, show }: ReminderProps) => {
    const [openModal, setOpenModal] = useState(false);
    const [formMode, setFormMode] = useState<FormMode>(null);

    const { notification } = App.useApp();
    const { Text } = Typography;
    const { currentUser } = useContext(UserContext);
    const { updateShowContext } = useShow();

    const addReminderHandle = async (formValues: ReminderFormValues) => {
        formValues.show = show;
        const newReminder = await addReminder(formValues, currentUser.token);
        updateShowContext(show, "reminder", newReminder);
        return `The reminder for ${show} has been added`;
    };

    const editReminderHandle = async (formValues: ReminderFormValues) => {
        formValues.show = show;
        const updatedReminder = await editReminder(formValues, currentUser.token);
        updateShowContext(show, "reminder", updatedReminder);
        return `The reminder for ${show} has been updated`;
    };

    const deleteReminderHandle = async () => {
        try {
            await deleteReminder(show, currentUser.token);
            updateShowContext(show, "reminder", null);
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
                    message = sessionExpiryMessage("delete this reminder");
                }
                else {
                    message = responseError.data.message;
                }
            }
            notification.error({
                message: `Unable to delete the reminder for ${show}`,
                description: message,
                duration: 8
            });
        }
    };


    const columns: TableColumnsType<Reminder> = [
        {
            key: "alert",
            dataIndex: "alert",
            title: "Reminder Alert",
        },
        {
            key: "warning_time",
            dataIndex: "warning_time",
            title: "Warning Time",
        },
        {
            key: "occasions",
            dataIndex: "occasions",
            title: "Occasions",
        },
        {
            key: "actions",
            title: "Actions",
            render: () => (
                <Dropdown menu={{ items: menuItems }} trigger={["click"]}>
                    <Button>Edit {show} Reminder</Button>
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
                    title={`Delete reminder for ${show}?`}
                    okText="Delete"
                    okButtonProps={{ style: { background: "#f00" } } }
                    onConfirm={deleteReminderHandle}
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
            <Text type="secondary">No reminder set for {show}</Text>
            <br />
            <Button onClick={() => openForm("add")}>Add Reminder</Button>
        </>
    );

    return (
        <>
            <Table 
                dataSource={reminder ? [reminder] : null}
                columns={currentUser ? columns : columns.filter(col => col.key !== "actions")}
                rowKey={(record: Reminder) => record.show}
                locale={{
                    emptyText: <EmptyTableView description={<EmptyDescription />} />
                }}
            />
            {openModal && (
                <ReminderForm
                    mode={formMode}
                    open={openModal}
                    show={reminder?.show || show}
                    closeModal={closeModal}
                    successHandler={formMode === "add" ? addReminderHandle : editReminderHandle}
                    initialValues={formMode === "edit" && reminder}
                />
            )}
        </>
    );
};

export { Reminder };