import { useContext, useEffect, useMemo, useRef, useState } from "react";
import { useHistory } from "react-router";
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

    const { currentUser, setUser } = useContext(UserContext);
    const intervalRef = useRef<NodeJS.Timeout>();
    const history = useHistory();

    const cookies = new Cookies(null, { path: "/" });

    const isTrackingSession = currentUser && cookies.get("user") ? true : false;

    const sessionTimeCheck = useMemo(() => {
        const interval = setInterval(() => {
            calculateSessionTime();
        }, 60000);
        return interval;
    }, [isTrackingSession]);

    useEffect(() => {
        calculateSessionTime();
        intervalRef.current = sessionTimeCheck;
        return () => clearInterval(intervalRef.current);
    }, []);

    useEffect(() => {
        if (!currentUser) {
            clearInterval(intervalRef.current);
        }
        else {
            intervalRef.current = sessionTimeCheck;
        }
    }, [currentUser]);

    useEffect(() => {
        console.log("sessionTime", sessionTime)
        if (sessionTime >= EXPIRY_TIME_MINUTES) {
            cookies.remove("user", { path: "/" });
            clearInterval(intervalRef.current);
        }
    }, [sessionTime]);

    const modalTitle = () => {
        if (sessionTime >= WARNING_TIME_MINUTES && sessionTime < EXPIRY_TIME_MINUTES) {
            return "Your session is about to expire";
        }
        else if (sessionTime >= EXPIRY_TIME_MINUTES) {
            return "Your session has expired";
        }
    };

    const calculateSessionTime = () => {
        const userCookie: Session = cookies.get("user");
        console.log("userCookie", userCookie)
        const loginTime = userCookie?.loginTime;

        if (loginTime) {
            console.log("loginTime", loginTime)
            setSessionTime(dayjs().diff(loginTime, "minutes"));
        }
    };

    const logout = () => {
        setSessionTime(0);
        clearInterval(intervalRef.current);
        cookies.remove("user", { path: "/" });
        setUser(null);
        history.push("/");
    };

    return (
        <Modal
            title={modalTitle()}
            open={isTrackingSession && sessionTime >= WARNING_TIME_MINUTES}
            maskClosable={false}
            closable={false}
            okText={sessionTime <= EXPIRY_TIME_MINUTES ? "Continue" : "Close"}
            onOk={() => console.log("session continued")}
            cancelText="Logout"
            onCancel={logout}
        >

        </Modal>
    );
};

export { SessionModal };