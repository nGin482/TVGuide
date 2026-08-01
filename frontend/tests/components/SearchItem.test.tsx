import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import axios, { AxiosResponse } from 'axios';
import { App } from "antd";
jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

import { SearchItem } from "../../src/components/SearchItem";
import { ShowsContext, UserContext } from "../../src/contexts";

import { currentUser, searchList, shows, user } from "../test_data";
import { SearchItem as TSearchItem } from "../../src/utils/types";

const mockSetShows = jest.fn();
const mockToggleStatus = jest.fn();
const mockSearchItem = jest.fn();

const SearchItemNoUser = (props: { searchItem?: TSearchItem }) => (
    <ShowsContext.Provider value={{ shows: shows, setShows: mockSetShows }}>
        <UserContext.Provider value={{ currentUser: null, setUser: null }}>
            <SearchItem
                searchItem={props?.searchItem}
                show="Doctor Who"
                setShowData={mockToggleStatus}
            />
        </UserContext.Provider>
    </ShowsContext.Provider>
);

const SearchItemUser = (props: { searchItem?: TSearchItem, displayActions?: boolean }) => (
    <App>
        <ShowsContext.Provider value={{ shows: shows, setShows: mockSetShows }}>
            <UserContext.Provider value={{ currentUser: currentUser, setUser: null }}>
                <SearchItem
                    searchItem={props.searchItem}
                    show="Doctor Who"
                    setShowData={mockToggleStatus}
                    displayActions={props.displayActions}
                />
            </UserContext.Provider>
        </ShowsContext.Provider>
    </App>
);

const notFoundResponse: AxiosResponse = {
    status: 404,
    statusText: "Not Found",
    data: {
        message: "No search item could be found for 'Doctor Who'",
    },
    headers: null,
    config: null
};

const response: AxiosResponse = {
    status: 200,
    statusText: "OK",
    data: shows[0].show_episodes,
    config: null,
    headers: null,
};

describe("Tests for SearchItem component", () => {
    beforeEach(() => {
        mockedAxios.get.mockClear();
        mockedAxios.delete.mockClear();
    });

    it("should display the search item in a table without actions when user is not signed in", () => {
        render(<SearchItemNoUser searchItem={searchList[0]} />);

        const table = screen.getByRole("table");
        const tableHeaders = screen.getAllByRole("columnheader");
        const tableCells = screen.getAllByRole("cell");

        expect(table).toBeInTheDocument();

        expect(tableHeaders[0].innerHTML).toContain("Search Active");
        expect(tableHeaders[1].innerHTML).toContain("Exact Title Match");
        expect(tableHeaders[2].innerHTML).toContain("Min Season Number");
        expect(tableHeaders[3].innerHTML).toContain("Max Season Number");
        expect(tableHeaders[4].innerHTML).toContain("Ignore Episodes");
        expect(tableHeaders[5].innerHTML).toContain("Ignore Seasons");
        expect(tableHeaders[6].innerHTML).toContain("Ignore Titles");

        expect(tableCells[0].innerHTML).toContain("Active");
        expect(tableCells[1].innerHTML).toContain("Exact Match");
        expect(tableCells[2].innerHTML).toContain("1");
        expect(tableCells[3].innerHTML).toContain("14");
        expect(tableCells[4].innerHTML).toContain("<ul></ul>");
        expect(tableCells[5].innerHTML).toContain("<ul></ul>");
        expect(tableCells[6].innerHTML).toContain("");
    });

    it("should display an inactive status when the search item is not active", () => {
        const searchItemCopy: TSearchItem = JSON.parse(JSON.stringify(searchList[0]));
        searchItemCopy.search_active = false;
        render(<SearchItemNoUser searchItem={searchItemCopy} />);

        const tableCells = screen.getAllByRole("cell");

        expect(tableCells[0].innerHTML).toContain("Inactive");
    });

    it("should show at the search item is checking all matches when exact match is false", () => {
        const searchItemCopy: TSearchItem = JSON.parse(JSON.stringify(searchList[0]));
        searchItemCopy.exact_title_match = false;
        render(<SearchItemNoUser searchItem={searchItemCopy} />);

        const tableCells = screen.getAllByRole("cell");

        expect(tableCells[1].innerHTML).toContain("Any matches");
    });

    it("should list the episode titles ignored", () => {
        const searchItemCopy: TSearchItem = JSON.parse(JSON.stringify(searchList[0]));
        searchItemCopy.conditions.ignore_episodes = ["Episode 1", "Episode 2"];
        render(<SearchItemNoUser searchItem={searchItemCopy} />);

        const tableCells = screen.getAllByRole("cell");

        expect(tableCells[4].innerHTML).toContain("Episode 1");
        expect(tableCells[4].innerHTML).toContain("Episode 2");
    });

    it("should list the seasons ignored", () => {
        const searchItemCopy: TSearchItem = JSON.parse(JSON.stringify(searchList[0]));
        searchItemCopy.conditions.ignore_seasons = [3, 4];
        render(<SearchItemNoUser searchItem={searchItemCopy} />);

        const tableCells = screen.getAllByRole("cell");

        expect(tableCells[5].innerHTML).toContain("Season 3");
        expect(tableCells[5].innerHTML).toContain("Season 4");
    });


    it("should display the actions column in the table when user is signed in", () => {
        render(<SearchItemUser searchItem={searchList[0]} displayActions />);

        const tableHeaders = screen.getAllByRole("columnheader");
        
        expect(tableHeaders[tableHeaders.length -1].innerHTML).toContain("Actions");
    });

    it("should display empty data when the show does not have a search item", () => {
        render(<SearchItemNoUser />);

        const emptyData = screen.getByText("No search item configured for Doctor Who");
        const createSearchItemButton = screen.queryByRole("button", { name: "Add Search Criteria" });

        expect(emptyData).toBeInTheDocument();
        expect(createSearchItemButton).not.toBeInTheDocument();
    });

    it("should show a button to add search items when the show does not have a search item and user is signed in", () => {
        render(<SearchItemUser />);

        const emptyData = screen.getByText("No search item configured for Doctor Who");
        const createSearchItemButton = screen.queryByRole("button", { name: "Add Search Criteria" });

        expect(emptyData).toBeInTheDocument();
        expect(createSearchItemButton).toBeInTheDocument();
    });

    it("should show a modal when the user clicks to create a search item", async () => {
        render(<SearchItemUser />);

        const createSearchItemButton = screen.queryByRole("button", { name: "Add Search Criteria" });

        act(() => {
            fireEvent.click(createSearchItemButton);
            mockedAxios.get.mockResolvedValue(response);
        });

        await waitFor(async () => {
            const modal = screen.getByRole("dialog");
            expect(modal).toBeInTheDocument();
        });
    });

    it("should close the modal presses cancel", async () => {
        render(<SearchItemUser displayActions />);

        const createSearchItemButton = screen.queryByRole("button", { name: "Add Search Criteria" });

        act(() => {
            fireEvent.click(createSearchItemButton);
            mockedAxios.get.mockResolvedValue(response);
        });

        const modal = screen.getByRole("dialog");
        const cancelButton = screen.getByRole("button", { name: "Cancel" });

        expect(modal).toBeInTheDocument();
        expect(cancelButton).toBeInTheDocument();

        await waitFor(async () => {
            fireEvent.click(cancelButton);
            expect(modal).not.toBeInTheDocument();
        });
    });

    it("should show a menu of items when the user clicks to edit the search item", async () => {
        const searchItemCopy: TSearchItem = JSON.parse(JSON.stringify(searchList[0]));
        render(<SearchItemUser searchItem={searchItemCopy} displayActions />);
        
        const editButton = screen.getByRole("button", { name: "Edit Doctor Who Search" });
        
        act(() => {
            fireEvent.click(editButton);
        });
        
        await waitFor(async () => {
            const menuItems = screen.getAllByRole("menuitem");
            expect(menuItems[0].innerHTML).toContain("Deactivate");
            expect(menuItems[1].innerHTML).toContain("Edit");
            expect(menuItems[2].innerHTML).toContain("Delete");
        });
    });

    it("should show the edit form when the user clicks the edit menu item", async () => {
        const searchItemCopy: TSearchItem = JSON.parse(JSON.stringify(searchList[0]));
        render(<SearchItemUser searchItem={searchItemCopy} displayActions />);
        
        const editButton = screen.getByRole("button", { name: "Edit Doctor Who Search" });
        
        act(() => {
            fireEvent.click(editButton);
            mockedAxios.get.mockResolvedValue(response);
        });
        const menuItems = screen.getAllByRole("menuitem");
        
        await waitFor(async () => {
            fireEvent.click(menuItems[1]);
            const modal = screen.getByRole("dialog");
            expect(modal).toBeInTheDocument();
            expect(modal.innerHTML).toContain("Edit Search Criteria for Doctor Who");
        });
    });

    it("should delete a search item", async () => {
        const searchItemCopy: TSearchItem = JSON.parse(JSON.stringify(searchList[0]));

        render(<SearchItemUser searchItem={searchItemCopy} displayActions />);

        const editButton = screen.getByRole("button", { name: "Edit Doctor Who Search" });

        act(() => {
            fireEvent.click(editButton);
        });

        const deleteItem = screen.getByText("Delete");

        act(() => {
            mockedAxios.delete.mockResolvedValue(notFoundResponse);
            fireEvent.click(deleteItem);
        });
        
        await waitFor(async () => {
            const confirmation = screen.getAllByText("Delete");
            fireEvent.click(confirmation[confirmation.length -1]);
            expect(mockedAxios.delete).toHaveBeenCalled();
        });
    });

    it("should handle errors when deleting a search item", async () => {
        // this test has no assertions
        const searchItemCopy: TSearchItem = JSON.parse(JSON.stringify(searchList[0]));

        render(<SearchItemUser searchItem={searchItemCopy} displayActions />);

        const editButton = screen.getByRole("button", { name: "Edit Doctor Who Search" });

        act(() => {
            fireEvent.click(editButton);
        });

        const deleteItem = screen.getByText("Delete");

        act(() => {
            mockedAxios.delete.mockImplementation(() => {
                throw Error("Testing error");
            });
            fireEvent.click(deleteItem);
        });
        
        await waitFor(async () => {
            const confirmation = screen.getAllByText("Delete");
            fireEvent.click(confirmation[confirmation.length -1]);
        });
    });
});