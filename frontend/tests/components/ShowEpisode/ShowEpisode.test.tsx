import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { App } from "antd";

import { ShowEpisodes } from "../../../src/components/ShowEpisode";
import { ShowsContext, UserContext } from "../../../src/contexts";
import {
  checkEpisodes,
  deleteShowEpisode,
  fetchLatestEpisodes,
  getEpisodes,
  getShowSeasons,
} from "../../../src/requests";
import { useShow } from "../../../src/hooks/useShow";
import { CurrentUser, ShowEpisode } from "../../../src/utils/types";

import { currentUser, shows } from "../../test_data";
import { testDoctorWhoEpisodes } from "../../test_data/showEpisodes";
import {
  testDoctorWhoTVMazeEpisodes,
  testDoctorWhoTVMazeSeasons,
} from "../../test_data/tvmaze";

jest.mock("../../../src/requests", () => ({
  checkEpisodes: jest.fn(),
  deleteShowEpisode: jest.fn(),
  fetchLatestEpisodes: jest.fn(),
  getEpisodes: jest.fn(),
  getShowSeasons: jest.fn(),
}));
jest.mock("../../../src/hooks/useShow", () => ({
  useShow: jest.fn(() => ({
    deleteEpisodeFromContext: jest.fn(),
  })),
}));

const mockGetEpisodes = jest.mocked(getEpisodes);
const mockGetShowSeasons = jest.mocked(getShowSeasons);
const mockSetShows = jest.fn();
const mockUseShow = jest.mocked(useShow);

const mockCheckEpisodes = jest.mocked(checkEpisodes);
const mockDeleteEpisode = jest.mocked(deleteShowEpisode);
const mockFetchLatestEpisodes = jest.mocked(fetchLatestEpisodes);

const ShowEpisodesNoUser = () => (
  <ShowsContext.Provider value={{ shows: shows, setShows: mockSetShows }}>
    <UserContext.Provider value={{ currentUser: null, setUser: null }}>
      <ShowEpisodes
        showName="Doctor Who"
        episodes={testDoctorWhoEpisodes}
      />
    </UserContext.Provider>
  </ShowsContext.Provider>
);

const ShowEpisodesUser = (
  props: { episodes?: ShowEpisode[], user?: CurrentUser }
) => (
  <ShowsContext.Provider value={{ shows: shows, setShows: mockSetShows }}>
    <UserContext.Provider value={{
      currentUser: props?.user ?? currentUser,
      setUser: null
    }}>
      <ShowEpisodes
        showName="Doctor Who"
        episodes={props?.episodes ?? testDoctorWhoEpisodes}
      />
    </UserContext.Provider>
  </ShowsContext.Provider>
);

describe("ShowEpisode component", () => {
  beforeAll(() => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: jest.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(), // Deprecated but required for older library pipelines
        removeListener: jest.fn(), 
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });


  it("displays a table of a show's episodes", async () => {
    render(<ShowEpisodesNoUser />);

    const table = screen.getByRole("table");
    const rows = screen.getAllByRole("row");

    expect(table).toBeInTheDocument();
    expect(rows).toHaveLength(4);

    const cells = within(rows[1]).getAllByRole("cell");

    expect(cells[0]).toHaveTextContent("1");
    expect(cells[1]).toHaveTextContent("1");
    expect(cells[2]).toHaveTextContent("Rose");
    expect(cells[3]).toHaveTextContent("");
    expect(cells[4]).toHaveTextContent("");
    expect(cells[5]).toHaveTextContent("ABC1");
    expect(cells[5]).toHaveTextContent("ABCHD");
    expect(cells[5]).toHaveTextContent("ABC2");
    expect(cells[6]).toHaveTextContent("01/01/2024");
  });

  it("changes seasons when the season buttons are pressed", async () => {
    render(<ShowEpisodesNoUser />);

    const season2 = screen.getByRole("button", { name: "Season 2" });
    fireEvent.click(season2);

    const rows = screen.getAllByRole("row");
    const cells = within(rows[1]).getAllByRole("cell");

    expect(cells[0]).toHaveTextContent("2");
    expect(cells[1]).toHaveTextContent("0");
    expect(cells[2]).toHaveTextContent("A Christmas Invasion");
  });

  it("fetches the show's latest episodes", async () => {
    mockCheckEpisodes.mockResolvedValueOnce({
      needs_refresh: true,
      latest_season_recorded: 1,
      tvmaze_season_max: 4,
    });

    render(<ShowEpisodesUser />);

    const checkEpisodesButton = screen.getByRole(
      "button",
      { name: "Check Episodes" }
    );
    fireEvent.click(checkEpisodesButton);

    await waitFor(() => {
      expect(mockFetchLatestEpisodes).toHaveBeenCalledWith(
        "Doctor Who",
        {
          needs_refresh: true,
          latest_season_recorded: 1,
          tvmaze_season_max: 4,
        },
      );
    });
  });

  it("opens a modal to edit an episode", async () => {
    mockGetShowSeasons.mockResolvedValueOnce(testDoctorWhoTVMazeSeasons);
    mockGetEpisodes.mockResolvedValueOnce(testDoctorWhoTVMazeEpisodes);

    render(
      <App>
        <ShowEpisodesUser />
      </App>
    );

    const rows = screen.getAllByRole("row");
    const cells = within(rows[1]).getAllByRole("cell");

    const dropdown = within(cells[cells.length-1]).getByRole(
      "button",
      { name: "Edit Episode" }
    );
    fireEvent.click(dropdown);

    const editMenuItem = await screen.findByRole("menuitem", { name: /edit/i });
    fireEvent.click(editMenuItem);

    const modal = await screen.findByRole("dialog");
    expect(modal).toBeInTheDocument();
  });

  it("deletes an episode", async () => {
    const mockDeleteEpisodeFromContext = jest.fn();
    mockDeleteEpisode.mockResolvedValueOnce();
  
    mockUseShow.mockReturnValue({
      addShowToContext: jest.fn(),
      deleteEpisodeFromContext: mockDeleteEpisodeFromContext,
      updateEpisodeContext: jest.fn(),
      updateShowContext: jest.fn(),
    });
    
    render(
      <App>
        <ShowEpisodesUser />
      </App>
    );

    const rows = await screen.findAllByRole("row");
    const cells = within(rows[1]).getAllByRole("cell");

    const dropdown = within(cells[cells.length-1]).getByRole(
      "button",
      { name: "Edit Episode" }
    );
    fireEvent.click(dropdown);

    const deleteMenuItem = await screen.findByRole(
      "menuitem",
      { name: /delete/i }
    );
    fireEvent.click(deleteMenuItem);

    const modal = await screen.findByRole("dialog");
    expect(modal).toBeInTheDocument();

    const confirmDeleteButton = await within(modal).findByRole(
      "button",
      { name: "Delete" }
    );
    fireEvent.click(confirmDeleteButton);

    const notification = await screen.findByText(
      `The episode "Rose" has been deleted`,
    );
    expect(notification).toBeInTheDocument();
    await waitFor(() => {
      expect(mockDeleteEpisode).toHaveBeenCalledWith(1);
      expect(mockDeleteEpisodeFromContext).toHaveBeenCalledWith(
        "Doctor Who",
        1
      );
    });
  });

  it("handles errors when deleting an episode", async () => {
    mockDeleteEpisode.mockImplementationOnce(() => {
      throw Error("Episode not found")
    });

    render(
      <App>
        <ShowEpisodesUser />
      </App>
    );

    const rows = screen.getAllByRole("row");
    const cells = within(rows[1]).getAllByRole("cell");

    const dropdown = within(cells[cells.length-1]).getByRole(
      "button",
      { name: "Edit Episode" }
    );
    fireEvent.click(dropdown);

    const deleteMenuItem = await screen.findByRole(
      "menuitem",
      { name: /delete/i }
    );
    fireEvent.click(deleteMenuItem);

    const modal = await screen.findByRole("dialog");
    const confirmDeleteButton = within(modal).getByRole(
      "button",
      { name: "Delete" }
    );
    fireEvent.click(confirmDeleteButton);

    const notification = await screen.findByText(
      `Unable to delete the episode "Rose"`,
    );
    expect(notification).toBeInTheDocument();
  });

  it("shows text when there are no episodes available", async () => {
    render(
      <ShowEpisodesUser
        episodes={[]}
      />
    );

    const emptyView = screen.getByText("No episodes found for Doctor Who");

    expect(emptyView).toBeInTheDocument();
  });

  it("hides the delete button if user is not admin", async () => {
    render(
      <ShowEpisodesUser
        user={{
          ...currentUser,
          role: "Standard",
        }}
      />
    );

    const rows = screen.getAllByRole("row");
    const cells = within(rows[1]).getAllByRole("cell");

    const dropdown = within(cells[cells.length-1]).getByRole(
      "button",
      { name: "Edit Episode" }
    );
    fireEvent.click(dropdown);

    const deleteMenuItems = await screen.findAllByRole("menuitem");
    expect(deleteMenuItems).toHaveLength(1);
  });
});
