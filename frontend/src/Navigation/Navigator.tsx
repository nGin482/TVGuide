import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { Breadcrumb } from "antd";
import type { ItemType } from "antd/es/breadcrumb/Breadcrumb";


const Navigator = () => {
    const [breadcrumbs, setBreadcrumbs] = useState(null);
    const location = useLocation();

    useEffect(() => {
        const paths = location.pathname.split("/");

        const breadcrumbs: ItemType[] = paths.map((path, idx) => {
            if (path === "") {
                return {
                    title: <NavLink to="/">Home</NavLink>
                };
            }
            else if (idx === paths.length -1) {
                return {
                    title: formatCrumb(path)
                };
            }
            else {
                const link = paths.slice(0, idx+1).join("/");
                return {
                    title: <NavLink to={link}>{formatCrumb(path)}</NavLink>
                };
            }
        });
        setBreadcrumbs(breadcrumbs);
    }, [location]);

    const formatCrumb = (crumb: string) => {
        if (crumb.includes("-")) {
            crumb = crumb.replace("-", " ");
        }
        return crumb.charAt(0).toUpperCase() + crumb.slice(1)
    };


    return (
        <Breadcrumb
            items={breadcrumbs}
            className="navigator"
        />
    );
};

export { Navigator };