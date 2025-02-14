import { ReactNode } from "react";
import { Empty } from "antd";

interface EmptyTableProps {
    description: ReactNode
}

const EmptyTableView = ({ description }: EmptyTableProps) => (
    <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description={description}
    />
);

export { EmptyTableView };