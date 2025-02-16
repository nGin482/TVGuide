import { act, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Switch, Route } from "react-router-dom";
import axios from "axios";

import { ShowEpisodes } from "../src/components/ShowEpisode";
import { ShowsContext, UserContext } from "../src/contexts";

import { currentUser, shows } from "./test_data";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

const ShowEpisodesPage = () => (
    <MemoryRouter initialEntries={[`/shows/Doctor Who`]}>
        <Switch>
            <Route path="/shows/:show">
            <ShowsContext.Provider value={{ shows, setShows: () => undefined }}>
                <UserContext.Provider value={{ currentUser: currentUser, setUser: () => undefined }}>
                    <ShowEpisodes
                        showName={shows[0].show_name}
                        episodes={shows[0].show_episodes}
                    />
                </UserContext.Provider>
            </ShowsContext.Provider>
            </Route>
        </Switch>
    </MemoryRouter>
);

describe('Viewing the details about a Recorded Show', () => {
        test('renders table with doctor who data', async () => {
        await act(async () => {
            mockedAxios.get.mockResolvedValue({ data: shows[0] });
            render(<ShowEpisodesPage />);
        });
        
        const table = screen.queryByTestId(/doctor who-table/i);
        expect(table).toBeInTheDocument();
    });

    test('renders buttons to change seasons', async () => {
        await act(async () => {
            mockedAxios.get.mockResolvedValue({ data: shows[0] });
            render(<ShowEpisodesPage />);
        });
        
        const seasonButtons = screen.queryAllByTestId(/season-/i);
        expect(seasonButtons[0]).toHaveTextContent('Season 1');
        expect(seasonButtons[1]).toHaveTextContent('Season 2');
    });

    test('clicking season button to change episodes in table', async () => {
        await act(async () => {
            mockedAxios.get.mockResolvedValue({ data: shows[0] });
            render(<ShowEpisodesPage />);
        });
        
        const seasonTwoButton = screen.queryByTestId(/season-2/i);
        fireEvent.click(seasonTwoButton);
        
        const table = screen.queryByTestId(/doctor who-table/i);
        expect(table).toHaveTextContent(/A Christmas Invasion/i);
        expect(table).not.toHaveTextContent(/Rose/i);
    });
});