import { useContext } from "react";
import { Form, Modal, Select } from "antd";

import { ShowsContext } from "../../contexts";
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
    const { showForm, userDetails, toggleModal, updateSubscriptionsHandle } = props;
    
    const { shows } = useContext(ShowsContext);

    const [ form ] = Form.useForm<{ shows: string[] }>();

    const createSubscriptionOptions = () => {
        const existingSearchSubscriptions = userDetails.show_subscriptions.map(
            sub => sub.search_item.show
        );
        const filteredShows = shows.filter(
            show => show.search_item && !existingSearchSubscriptions.includes(show.search_item.show)
        );
        return filteredShows.map(show => ({
            label: show.show_name,
            value: show.show_name
        }));
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
            onOk={subscribe}
            onCancel={toggleModal}
            closeIcon={false}
        >
            <Form
                form={form}
                name="add_show_subscription"
            >
                <Form.Item name="shows" label="Select shows to subscribe to">
                    <Select
                        options={createSubscriptionOptions()}
                        showSearch
                        mode="multiple"
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
};

export { SubscriptionForm };