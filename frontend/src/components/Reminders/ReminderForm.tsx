import { useState } from "react";
import type { FormEvent } from "react";
import { App, Form, Modal, Input, Select, Typography, Alert } from "antd";

import { sessionExpiryMessage } from "../../utils";
import { ErrorResponse, FormMode, Reminder } from "../../utils/types";


interface ReminderFormProps {
    mode: FormMode
    open: boolean
    show: string
    closeModal: () => void
    successHandler: (data: ReminderFormValues) => Promise<string>
    initialValues?: Reminder
}

interface ReminderFormValues extends Partial<Reminder> {}

const ReminderForm = ({ mode, open, show, closeModal, successHandler, initialValues }: ReminderFormProps) => {
    const [reminderAlert, setReminderAlert] = useState<string>(null);
    const [errorState, setErrorState] = useState(false);

    const { notification } = App.useApp();
    const [form] = Form.useForm<ReminderFormValues>();
    const { Text } = Typography;

    const convertWarningTimeToNumber = (event: FormEvent<HTMLInputElement>) => {
        let warningTimeString = event.currentTarget.value;
        const lastCharIndex = warningTimeString.length - 1;
        if (warningTimeString.charCodeAt(lastCharIndex) < 48 || warningTimeString.charCodeAt(lastCharIndex) > 57) {
            warningTimeString = warningTimeString.replace(warningTimeString.slice(-1), '');
        }
        if (warningTimeString === '') {
            return '';
        }
        return Number(warningTimeString);
    };


    const submitReminder = async () => {
        if (!form.getFieldValue("warning_time")) {
            form.setFieldValue("alert", "During");
            form.setFieldValue("warning_time", 0);
        }
        try {
            await form.validateFields();
            setErrorState(false);
        }
        catch(error) {
            console.log(error)
            setErrorState(true);
        }
        
        try {
            const formValues = form.getFieldsValue();
            console.log(formValues)
            const result = await successHandler(formValues);
            notification.success({
                message: "Success!",
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
                    message = sessionExpiryMessage("add this reminder");
                }
                else {
                    message = responseError.data.message;
                }
            }
            notification.error({
                message: `Unable to ${mode} reminder for ${show}`,
                description: message,
                duration: 8
            });
        }
    };

    return (
        <Modal
            open={open}
            onOk={submitReminder}
            onCancel={closeModal}
            okText="Submit"
            title={`${mode[0].toUpperCase() + mode.slice(1)} Reminder for ${show}`}
        >
            <Form
                form={form}
                name="reminder-form"
                initialValues={initialValues}
            >
                <Form.Item
                    name="alert"
                    label="Remind me"
                    initialValue="Before"
                >
                    <Select
                        options={[
                            { label: 'Before the episode starts', value: 'Before' },
                            { label: 'When the episode starts', value: 'During' },
                            { label: 'After the episode starts', value: 'After' }
                        ]}
                        onChange={(value) => setReminderAlert(value)}
                    />
                </Form.Item>
                <Form.Item
                    name="warning_time"
                    label="How much warning time"
                    rules={[
                        {
                            required: reminderAlert === "During" ? false : true,
                            min: 0,
                            max: 60,
                            type: 'number',
                            message: 'Please enter a value between 0 and 60'
                        }
                    ]}
                    getValueFromEvent={convertWarningTimeToNumber}
                >
                    <Input
                        disabled={reminderAlert === 'During'}
                        addonAfter="minutes"
                    />
                    {reminderAlert === 'During' && (
                        <Text type="secondary">
                            This does not need to be set if you wish to be reminded when the episode starts.
                        </Text>
                    )}
                </Form.Item>
                <Form.Item
                    name="occasions"
                    label="Remind me for"
                    initialValue="All"
                >
                    <Select
                        options={[
                            { label: 'Every episode', value: 'All' },
                            { label: 'Only the latest seasons', value: 'Latest' }
                        ]}
                    />
                </Form.Item>
                {errorState && (
                    <Alert
                        type="error"
                        message="There are errors in the form"
                        description="Please resolve the errors before submitting again"
                    />
                )}
            </Form>
        </Modal>
    )

};

export { ReminderForm };