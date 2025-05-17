import { useContext, useEffect, useRef, useState } from "react";
import { Modal } from "antd";
import dayjs from "dayjs";
import Cookies from "universal-cookie";

import { UserContext } from "../../contexts";
import { Session } from "../../utils/types";

const WARNING_TIME_MINUTES = 4;
const EXPIRY_TIME_MINUTES = 5;

// only show if user is logged in

const SessionModal = () => {
    const [sessionTime, setSessionTime] = useState(0);

    const { setUser } = useContext(UserContext);
    const intervalRef = useRef<NodeJS.Timeout>();

    const cookies = new Cookies(null, { path: "/" });

    useEffect(() => {
        const remainingTimeCheck = setInterval(() => {
            calculateSessionTime();
        }, 60000);

        intervalRef.current = remainingTimeCheck;
        return () => clearInterval(intervalRef.current);
    }, []);

    useEffect(() => {
        console.log("sessionTime", sessionTime)
        if (sessionTime >= EXPIRY_TIME_MINUTES) {
            logout();
            clearInterval(intervalRef.current);
        }
    }, [sessionTime]);

    const calculateSessionTime = () => {
        const userCookie: Session = cookies.get("user");
        console.log("userCookie", userCookie)
        const loginTime = userCookie.loginTime;
        console.log("loginTime", loginTime)
        
        setSessionTime(dayjs().diff(loginTime, "minutes"));
    };

    const logout = () => {
        cookies.remove("user");
        setUser(null);
    };

    return (
        <Modal
            title="Session is about to expire"
            open={sessionTime >= WARNING_TIME_MINUTES}
            maskClosable={false}
            closable={false}
            onOk={() => console.log("session continued")}
            cancelText="Logout"
            onCancel={logout}
        >

        </Modal>
    );
};

export { SessionModal };