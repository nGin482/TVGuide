import { useEffect, useState } from "react";
import { Modal } from "antd";

const WARNING_TIME_MINUTES = 4;
const EXPIRY_TIME_MINUTES = 5;

const SessionModal = () => {
    const [remainingTime, setRemainingTime] = useState(EXPIRY_TIME_MINUTES);

    useEffect(() => {
        const remainingTimeCheck = setInterval(() => {
            setRemainingTime(current => current - 1);
        }, 15000);

        if (remainingTime <= 0) {
            clearInterval(remainingTimeCheck);
        }
    }, []);

    useEffect(() => {
        console.log("remainingTime", remainingTime)
    }, [remainingTime])

    return (
        <Modal
            title="Session is about to expire"
            open={remainingTime <= WARNING_TIME_MINUTES}
            maskClosable={false}
            closable={false}
            onOk={() => setRemainingTime(EXPIRY_TIME_MINUTES)}
        >

        </Modal>
    );
};

export { SessionModal };