import { useState } from "react";
import { Helmet } from "react-helmet";
import { Button } from "antd";

import Login from "../components/Login";
import RegisterUser from "../components/Registration/RegisterUser";

const LoginPage = () => {
    const [activity, setActivity] = useState('login');

    return (
        <>
            {activity === 'login' && (
                <>
                    <Helmet>
                        <title>Login | TVGuide</title>
                    </Helmet>
                    <Login />
                    <br/>
                    Don't have an account? <Button type="primary" onClick={() => setActivity('register')}>Register</Button>
                </>
            )}
            {activity === 'register' && (
                <>
                    <Helmet>
                        <title>Sign Up | TVGuide</title>
                    </Helmet>
                    <RegisterUser />
                    <br />
                    Already have an account? <Button type="primary" onClick={() => setActivity('login')}>Log in</Button>
                </>
            )}
        </>
    );
};

export default LoginPage;