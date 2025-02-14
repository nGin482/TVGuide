import { LeftOutlined, RightOutlined } from "@ant-design/icons";

interface SlickArrowProps {
    className: string
    currentSlide: number
    onClick: () => {}
    style: {}
    children: JSX.Element
};

const ArrowComponent = (props: SlickArrowProps) => {
    const { className, style, onClick, children } = props;
    return (
        <div
            className={className}
            style={{
                ...style,
                color: 'black',
                fontSize: '15px',
                lineHeight: '1.5715'
            }}
            onClick={onClick}
        >
            {children}
        </div>
    );
};

const PrevArrow = (props) => (
    <ArrowComponent {...props}>
        <LeftOutlined />
    </ArrowComponent>
);

const NextArrow = (props) => (
    <ArrowComponent {...props}>
        <RightOutlined />
    </ArrowComponent>
);

export { PrevArrow, NextArrow };