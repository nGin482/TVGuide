import { Editor } from "@tiptap/react";
import {
    BoldOutlined,
    ItalicOutlined,
    StrikethroughOutlined,
    UnderlineOutlined
} from "@ant-design/icons";

import "./styles/toolbar.style.scss";

interface ToolBarProps {
    editor: Editor
}

const ToolBar = ({ editor }: ToolBarProps) => (
    <div className="toolbar">
        <button
            onClick={() => editor.chain().focus().toggleBold().run()}
            className={editor.isActive("bold") ? "is-active" : ""}
        >
            <BoldOutlined />
        </button>
        <button
            onClick={() => editor.chain().focus().toggleItalic().run()}
            className={editor.isActive("italic") ? "is-active" : ""}
        >
            <ItalicOutlined />
        </button>
        <button
            onClick={() => editor.chain().focus().toggleUnderline().run()}
            className={editor.isActive("underline") ? "is-active" : ""}
        >
            <UnderlineOutlined />
        </button>
        <button
            onClick={() => editor.chain().focus().toggleStrike().run()}
            className={editor.isActive("strike") ? "is-active" : ""}
        >
            <StrikethroughOutlined />
        </button>
    </div>
);

export { ToolBar };