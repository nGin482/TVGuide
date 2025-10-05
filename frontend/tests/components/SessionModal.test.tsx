import { act, fireEvent, render, screen } from "@testing-library/react";
import axios, { AxiosResponse } from "axios";
import dayjs from "dayjs";

import { MockCookies, mockGetCookie, mockRemoveCookie, mockSetCookie } from "../mocks/mockCookie";
jest.mock("universal-cookie", () => MockCookies);
const mockHistoryPush = jest.fn();
jest.mock('react-router', () => ({
    useHistory: () => ({
        push: mockHistoryPush,
    }),
}));

import { SessionModal } from "../../src/components/SessionModal";
import { UserContext } from "../../src/contexts";

import { currentUser } from "../test_data";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

const TestSessionModalWithoutUser = () => (
    <UserContext.Provider value={{ currentUser: null, setUser: () => undefined }}>
        <SessionModal />
    </UserContext.Provider>
);

const TestSessionModalWithUser = () => (
    <UserContext.Provider value={{ currentUser: currentUser, setUser: () => undefined }}>
        <SessionModal />
    </UserContext.Provider>
);


describe("Tests for SessionModal component", () => {
    beforeEach(() => {
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    it("should not display the session modal if the user is not logged in", async () => {
        render(<TestSessionModalWithoutUser />);

        act(() => {
            jest.advanceTimersByTime(240000);
        });

        const modalTitle = screen.queryByText("session is about to expire");

        expect(modalTitle).not.toBeInTheDocument();
    });

    it("should display the session modal if the user is logged in and their session is about to expire", async () => {
        mockGetCookie.mockReturnValue({
            username: "Test User",
            role: "User",
            loginTime: dayjs().toString(),
        });
        const { rerender } = render(<TestSessionModalWithUser />);

        act(() => {
            jest.advanceTimersByTime(240000);
        });

        rerender(<TestSessionModalWithUser />);
        
        const modalTitle = screen.getByRole("dialog", { name: "Your session is about to expire" });
        const logoutButton = screen.getByRole("button", { name: "Logout" });
        const continueSessionButton = screen.getByRole("button", { name: "Continue Session" });

        expect(modalTitle).toBeInTheDocument();
        expect(logoutButton).toBeInTheDocument();
        expect(continueSessionButton).toBeInTheDocument();
    });

    it("should display the session modal if the user's session has expired", async () => {
        mockGetCookie.mockReturnValue({
            username: "Test User",
            role: "User",
            loginTime: dayjs().toString(),
        });
        const { rerender } = render(<TestSessionModalWithUser />);

        act(() => {
            jest.advanceTimersByTime(300000);
        });

        rerender(<TestSessionModalWithUser />);
        
        const modalTitle = screen.getByRole("dialog", { name: "Your session has expired" });
        const logoutButton = screen.getByRole("button", { name: "Logout" });
        const continueSessionButton = screen.queryByRole("button", { name: "Continue Session" });

        expect(modalTitle).toBeInTheDocument();
        expect(logoutButton).toBeInTheDocument();
        expect(continueSessionButton).not.toBeInTheDocument();
    });

    it("should allow the user to continue their session if it is about to expire", async () => {
        mockGetCookie.mockReturnValue({
            username: "Test User",
            role: "User",
            loginTime: dayjs().toString(),
        });
        const response: AxiosResponse = {
            status: 200,
            statusText: 'OK',
            data: {
                username: "Test User",
                role: "User",
            },
            headers: null,
            config: null
        };
        mockedAxios.post.mockResolvedValue(response);

        const { rerender } = render(<TestSessionModalWithUser />);

        act(() => {
            jest.advanceTimersByTime(240000);
        });

        act(() => {
            rerender(<TestSessionModalWithUser />);
        });
        
        const continueSessionButton = screen.getByRole("button", { name: "Continue Session" });

        expect(continueSessionButton).toBeInTheDocument();

        await act(async() => {
            fireEvent.click(continueSessionButton);
        });

        expect(axios.post).toHaveBeenCalledWith(
            "https://tvguide-ng-test.com/api/auth/refresh",
            null,
            {
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-CSRF-Token": undefined
                },
                withCredentials: true
            }
        );
        expect(mockSetCookie).toHaveBeenCalled();
    });

    it("should allow the user to log out of their session if it is about to expire", async () => {
        mockGetCookie.mockReturnValue({
            username: "Test User",
            role: "User",
            loginTime: dayjs().toString(),
        });
        const response: AxiosResponse = {
            status: 200,
            statusText: 'OK',
            data: {
                username: "Test User",
                role: "User",
            },
            headers: null,
            config: null
        };
        mockedAxios.post.mockResolvedValue(response);

        const { rerender } = render(<TestSessionModalWithUser />);

        act(() => {
            jest.advanceTimersByTime(240000);
        });

        act(() => {
            rerender(<TestSessionModalWithUser />);
        });
        
        const logoutButton = screen.getByRole("button", { name: "Logout" });

        expect(logoutButton).toBeInTheDocument();

        await act(async() => {
            fireEvent.click(logoutButton);
        });

        expect(axios.post).toHaveBeenCalledWith(
            "https://tvguide-ng-test.com/api/auth/logout",
            null,
            {
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-CSRF-Token": undefined
                },
                withCredentials: true
            }
        );
        expect(mockRemoveCookie).toHaveBeenCalled();
        expect(mockHistoryPush).toHaveBeenCalledWith("/");
    });
});