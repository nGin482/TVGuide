import { Tag } from "antd";

interface StatusTagProps {
    status: string
}


const ShowStatusTag = ({ status }: StatusTagProps) => {

    const tagColour = () => {
        switch(status) {
            case 'Ended':
                return 'error';
            case 'Running':
                return 'success';
            default:
                return 'processing'
        }
    };

    return (
        <Tag color={tagColour()}>{status}</Tag>
    );
};

export default ShowStatusTag;