import { useContext } from "react";
import { Helmet } from "react-helmet";
import { App, Button, Divider, Flex, Form, Input, Typography } from "antd";

import { UserContext } from "../contexts";
import { changePassword } from "../requests";
import { sessionExpiryMessage } from "../utils";
import { AccountDetailsFormValues, CurrentUser } from "../utils/types";
import "../styles/ProfileSettingsPage.css";

interface SettingsProps {
    user: CurrentUser
};


const ProfileSettingsPage = ({ user }: SettingsProps) => {

    const { setUser } = useContext(UserContext);
    const { notification } = App.useApp();
    const { Title } = Typography;

    const changeDetailsHandle = async (values: AccountDetailsFormValues) => {
        try {
            const updatedDetails = await changePassword(user.username, values, user.token);
            setUser(current => ({ ...updatedDetails, token: current.token }));
            notification.success({
                message: "Success!",
                description: "Your password has been updated"
            });
        }
        catch(error) {
            let message = error?.message;
            if (error?.response) {
                message = error?.response?.data?.msg
                    ? sessionExpiryMessage("change your password")
                    : error?.response?.data?.message;
            }
            notification.error({
                message: "An error occurred updating your password",
                description: message
            });
        }
    };


    return (
        <>
            <Helmet>
                <title>Your Settings | TVGuide</title>
            </Helmet>
            <Title level={3}>
                {user.username}
            </Title>
            <Divider />
            <Flex justify="space-around" className="account-settings-wrapper">
                <div id="change-details">
                    <h5>Change Account Details</h5>
                    <Form
                        onFinish={changeDetailsHandle}
                    >
                        <Form.Item
                            label="Change Username"
                            name="username"
                        >
                            <Input />
                        </Form.Item>
                        <Form.Item
                            label="Change Password"
                            name="password"
                        >
                            <Input.Password />
                        </Form.Item>
                        <Form.Item>
                            <Button htmlType="submit" type="primary">Submit</Button>
                        </Form.Item>
                    </Form>
                </div>
                <div id="delete-account-section">
                    <Title level={4}>Delete Your Account</Title>
                    <p>Please be certain before deleting your account.
                        <br/>
                        NOTE: Any shows or reminders you have requested to be added will not be deleted as these are used for all users.
                    </p>
                    <Button danger type="primary" className="delete-account">Delete Account</Button>
                </div>
            </Flex>
            
            {user.role !== 'Admin' && (
                <>
                    <Divider orientation="left">Request Administrator Access</Divider>
                    <div id="admin-access-request-section">
                        <p>
                            Administrators are able to make changes to:
                            <ul>
                                <li>search items</li>
                                <li>reminders</li>
                                <li>details about shows and episodes recorded</li>
                            </ul>
                            A request will need to be approved by another admin in order for administration access to be granted
                        </p>
                        <Button id="admin-access-request">Request</Button>
                    </div>
                </>
            )}
        </>
    );
};

export default ProfileSettingsPage;