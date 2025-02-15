import { useContext } from "react";
import { Form, Modal, Select } from "antd";

import { ShowsContext, UserContext } from "../../contexts";
import { SubscriptionsAction, SubscriptionsPayload, User } from "../../utils/types";


interface SubscriptionFormProps {
    showForm: boolean
    userDetails: User
    toggleModal: () => void
    updateSubscriptionsHandle: (
        payload: SubscriptionsPayload,
        action: SubscriptionsAction
    ) => Promise<void>
}

const SubscriptionForm = (props: SubscriptionFormProps) => {
    const { showForm, toggleModal, updateSubscriptionsHandle } = props;
    
    const { shows } = useContext(ShowsContext);
    const { currentUser } = useContext(UserContext);

    const [ form ] = Form.useForm<{ shows: string[] }>();

    const setSelectOptions = () => {
        const filteredShows = shows.filter(show => show.search_item);
        return filteredShows.map(show => ({ label: show.show_name, value: show.show_name }));
    };

    const subscribe = async () => {
        const payload: SubscriptionsPayload = {
            subscribe: {
                show_subscriptions: form.getFieldValue("shows")
            }
        };
        updateSubscriptionsHandle(payload, "subscribe");
        toggleModal();
    };


    return (
        <Modal
            open={showForm}
            okText="Submit"
            onOk={() => subscribe()}
            onCancel={toggleModal}
            closeIcon={false}
        >
            <Form
                form={form}
                name="add_show_subscription"
            >
                <Form.Item name="shows" label="Select shows to subscribe to">
                    <Select
                        options={setSelectOptions()}
                        showSearch
                        mode="multiple"
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
};

export { SubscriptionForm };