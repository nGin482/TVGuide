import { Tag } from "antd";

import { SearchItem } from "../../utils/types";

interface SearchItemTagProps {
    searchItem: SearchItem
}

const SearchItemTag = ({ searchItem }: SearchItemTagProps) => {
    if (searchItem && searchItem.search_active) {
        return <Tag color="success">Search active</Tag>;
    }
    else if (searchItem && !searchItem.search_active) {
        return <Tag color="orange">Search inactive</Tag>;
    }
    else {
        return <Tag color="error">No search</Tag>;
    }
};

export { SearchItemTag };