import { useContext } from 'react';
import { App, Button, Form, Input, Select } from 'antd';

import { ShowsContext } from '../../contexts';
import { registerNewUser } from '../../requests';
import { NewUserDetails } from '../../utils/types';
import './RegisterUser.css';

const RegisterUser = () => {
    const { shows } = useContext(ShowsContext);
    const { notification } = App.useApp();
    const [form] = Form.useForm<NewUserDetails>();
    
    const registerUser = async (values: NewUserDetails) => {
        if (!values.show_subscriptions) {
            values.show_subscriptions = [];
        }
        
        try {
            const registedUser = await registerNewUser(values);
            notification.success({
                message: "Success!",
                description: "Your account has successfully been created."
            });
        }
        catch(error) {
            let message = error.message;
            if (error?.response) {
                message = error.response?.data?.message;
            }
            notification.error({
                message: "There was a problem registering your account",
                description: message
            });
        }
    };
    
    return (
        <Form
            onFinish={registerUser}
            id="register-user"
            form={form}
        >
            <Form.Item
                label="Username"
                name="username"
                required
            >
                <Input />
            </Form.Item>
            <Form.Item
                label="Password"
                name="password"
                required
            >
                <Input.Password />
            </Form.Item>
            <Form.Item
                label="Show Subscriptions"
                name="show_subscriptions"
            >
                <Select
                    options={
                        shows
                        ? shows.map(show => ({ label: show.show_name, value: show.show_name }))
                        : []
                    }
                    showSearch
                    notFoundContent='No Shows available'
                    mode="multiple"
                />
            </Form.Item>
            <Button type="primary" htmlType="submit">Register</Button>
        </Form>
    );
};

export default RegisterUser;