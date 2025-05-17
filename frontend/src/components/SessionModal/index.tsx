import { useEffect, useRef, useState } from "react";
import { Modal } from "antd";
import dayjs from "dayjs";
import Cookies from "universal-cookie";
import { Session } from "../../utils/types";

const WARNING_TIME_MINUTES = 4;
const EXPIRY_TIME_MINUTES = 5;

// only show if user is logged in

const SessionModal = () => {
    const [remainingTime, setRemainingTime] = useState(EXPIRY_TIME_MINUTES);

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
        console.log("remainingTime", remainingTime)
        if (remainingTime <= 0) {
            clearInterval(intervalRef.current);
        }
    }, [remainingTime]);

    const calculateSessionTime = () => {
        const userCookie: Session = cookies.get("user");
        console.log("userCookie", userCookie)
        const loginTime = userCookie.loginTime;
        console.log("loginTime", loginTime)
        
        console.log("minutes elapsed", dayjs().diff(loginTime, "minutes"))
        return dayjs().diff(loginTime, "minutes")
    };

    return (
        <Modal
            title="Session is about to expire"
            open={calculateSessionTime() >= WARNING_TIME_MINUTES}
            maskClosable={false}
            closable={false}
            onOk={() => setRemainingTime(EXPIRY_TIME_MINUTES)}
        >

        </Modal>
    );
};

export { SessionModal };