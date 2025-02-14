import { EditorContent, useEditor } from "@tiptap/react";
import Underline from "@tiptap/extension-underline";
import StarterKit from "@tiptap/starter-kit";

import { ToolBar } from "./ToolBar";
import { ShowEpisode } from "../../utils/types";
import "./styles/editor.style.scss";


interface EditorProps {
    content: string
    updateContent: (field: keyof ShowEpisode, value: string) => void
}

const CustomEditor = ({ content, updateContent }: EditorProps) => {
    // const [content, setContent] = useState<EditorState>(null);

    // const updateContent = (state: EditorState) => {
    //     setContent(state);
    // };

    const extensions = [
        StarterKit.configure({ 
            heading: {
                levels: [1, 2, 3, 4, 5, 6]
            }
        }),
        Underline,
    ];

    const editor = useEditor({
        extensions,
        content,
        onUpdate: () => {
            updateContent("summary", editor.getHTML())
        }
    });

    return (
        <div className="editor">
            <ToolBar editor={editor} />
            <EditorContent editor={editor} />
        </div>
    );
};

export { CustomEditor };