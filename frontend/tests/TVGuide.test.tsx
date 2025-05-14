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

    test("renders an error alert if no guide is returned", async () => {
        const { getByRole } = render(<TVGuide />);
        
        await waitFor(() => {
            const error = getByRole("alert");
            expect(error).toBeInTheDocument();
            expect(error.innerHTML).toContain(
                `There was a problem fetching the guide for ${dayjs().format("DD MMMM YYYY")}`
            );
            expect(error.innerHTML).toContain(
                "There is a problem communicating with the server"
            );
        });
    });

    test("renders an error alert if no guide is found for the date chosen", async () => {
        const noGuideResponse: AxiosResponse = JSON.parse(JSON.stringify(response));
        noGuideResponse.status = 404;
        noGuideResponse.statusText = "Not Found";
        noGuideResponse.data = {
            message: "There is no guide for this date"
        };
                
        mockedAxios.get.mockRejectedValue({ response: noGuideResponse });

        const { getByRole } = render(<TVGuide />);
        
        await waitFor(() => {
            const error = getByRole("alert");
            expect(error).toBeInTheDocument();
            expect(error.innerHTML).toContain(
                `There was a problem fetching the guide for ${dayjs().format("DD MMMM YYYY")}`
            );
            expect(error.innerHTML).toContain("There is no guide for this date");
        });
    });

    test("renders a datepicker to choose a different date", async () => {
        response.data = guide;              
        mockedAxios.get.mockResolvedValue(response);
        
        const { getByRole } = render(<TVGuide />);

        const datePicker = getByRole("textbox");
        expect(datePicker).toBeInTheDocument();
    });

    test("datepicker changes date displayed", async () => {
        response.data = guide;              
        mockedAxios.get.mockResolvedValue(response);
        
        const { getByRole, rerender } = render(<TVGuide />);

        const previousDay = dayjs().subtract(1, "day");

        const datePicker = getByRole("textbox");
        expect(datePicker).toBeInTheDocument();
        fireEvent.mouseDown(datePicker);
        fireEvent.change(datePicker, { target: { value: previousDay.format("YYYY-MM-DD") } });
        expect(datePicker).toHaveValue(previousDay.format("YYYY-MM-DD"));
        
        await waitFor(() => {
            rerender(<TVGuide />);

            const dateHeader = getByRole("heading");
            expect(dateHeader).toBeInTheDocument();
        });
        
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
