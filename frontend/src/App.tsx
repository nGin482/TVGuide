import { BrowserRouter } from 'react-router-dom';
import { App as AntdApp, ConfigProvider, ThemeConfig } from 'antd';

import NavigationHandle from './Navigation/NavigationHandle';
import BasePage from './Pages/BasePage';
import { SessionModal } from './components/SessionModal';
import { ContextWrapper } from "./contexts";

const theme: ThemeConfig = {
    token: {
        colorPrimary: '#00b96b'
    }
};

function App() {

    return (
        <ConfigProvider theme={theme}>
            <BrowserRouter>
                <AntdApp>
                    <ContextWrapper>
                        <SessionModal />
                        <BasePage />
                        <NavigationHandle/>
                    </ContextWrapper>
                </AntdApp>
            </BrowserRouter>
        </ConfigProvider>
    );
};

export default App;
