import { useContext, useEffect, useMemo, useRef, useState } from "react";
import { useHistory } from "react-router";
import { Modal } from "antd";
import dayjs from "dayjs";
import Cookies from "universal-cookie";

import { logoutSession, refreshSession } from "../../requests";
import { UserContext } from "../../contexts";
import { Session } from "../../utils/types";

const WARNING_TIME_MINUTES = 4;
const EXPIRY_TIME_MINUTES = 5;

// new token when continuing session
// hide "continue session" button when session has expired

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

    const handleRefreshSession = async () => {
        const response = await refreshSession();
        setUser(response);
        setSessionTime(0);
        cookies.set('user', JSON.stringify({ ...response, loginTime: dayjs() }));
        clearInterval(intervalRef.current);
        intervalRef.current = setInterval(() => {
            calculateSessionTime();
        }, 60000);
    };

    const logout = async () => {
        setSessionTime(0);
        clearInterval(intervalRef.current);
        await logoutSession();
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
            okText="Continue Session"
            onOk={handleRefreshSession}
            okButtonProps={{
                style: {
                    display: sessionTime >= EXPIRY_TIME_MINUTES && "none"
                }
            }}
            cancelText="Logout"
            onCancel={logout}
        />
    );
};

export { SessionModal };