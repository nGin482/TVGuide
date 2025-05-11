import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import axios, { AxiosResponse } from 'axios';
import dayjs from 'dayjs';

import TVGuide from '../src/components/TVGuide';

import { currentUser, guide } from './test_data';

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

const response: AxiosResponse = {
    status: 200,
    statusText: 'OK',
    data: null,
    headers: null,
    config: null
};

describe("test TVGuide component", () => {
    beforeEach(() => {
        jest.resetAllMocks();
    });

    test("renders guide data", async () => {
        response.data = guide;
                
        mockedAxios.get.mockResolvedValue(response);
        
        const { getByRole } = render(<TVGuide />);

        const dateHeader = screen.getByRole("heading");
        expect(dateHeader).toBeInTheDocument();
        expect(dateHeader.innerHTML).toContain(dayjs().format("DD MMMM YYYY"));
        
        await waitFor(() => expect(getByRole("table")).toBeInTheDocument());
    });

    test('TVGuide only renders shows user has subscribed to', async () => {
        response.data = guide;              
        mockedAxios.get.mockResolvedValue(response);
        
        render(<TVGuide user={currentUser} />);
        
        await waitFor(() => {
            const maigret = screen.queryAllByText(/Maigret/i);
            const deathInParadise = screen.queryByText(/Death in Paradise/i);
            const vera = screen.queryByText(/Vera/i);
            const lewis = screen.queryByText(/Lewis/i);
    
            expect(maigret[0]).toBeInTheDocument();
            expect(deathInParadise).not.toBeInTheDocument();
            expect(vera).not.toBeInTheDocument();
            expect(lewis).not.toBeInTheDocument();
        });
    });
});
