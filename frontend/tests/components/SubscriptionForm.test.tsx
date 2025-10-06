import { act, fireEvent, render, screen } from "@testing-library/react";

import { SubscriptionForm } from "../../src/components/SubscriptionForm";
import { ShowsContext } from "../../src/contexts";

import { shows, user } from "../test_data";

const mockToggleModal = jest.fn();
const mockUpdateSubscriptions = jest.fn();

const SubscriptionFormWithShows = () => (
    <ShowsContext.Provider value={{ shows: shows, setShows: null }}>
        <SubscriptionForm
            showForm={true}
            userDetails={user}
            toggleModal={mockToggleModal}
            updateSubscriptionsHandle={mockUpdateSubscriptions}
        />
    </ShowsContext.Provider>
);


describe("Tests for Search subscription form", () => {
    it("should show a form with a dropdown", () => {
        render(<SubscriptionFormWithShows />);

        const dropdown = screen.getByRole("combobox");
        
        expect(dropdown).toBeInTheDocument();
    });

    it("should shows available shows to subscribe to", async () => {
        render(<SubscriptionFormWithShows />);

        const combobox = screen.getByRole("combobox");

        await act(async () => {
            fireEvent.mouseDown(combobox);
        });

        const options = screen.getByRole("listbox");
        expect(options).toBeInTheDocument();
        expect(options.innerHTML).toContain("The Crown");
    });

    it("should filter out shows that don't have a search item", async () => {
        render(<SubscriptionFormWithShows />);

        const combobox = screen.getByRole("combobox");

        await act(async () => {
            fireEvent.mouseDown(combobox);
        });

        const options = screen.getByRole("listbox");
        expect(options).toBeInTheDocument();
        expect(options.innerHTML).not.toContain("Person of Interest");
    });

    it("should filter out shows that the user has already subscribed to", async () => {
        render(<SubscriptionFormWithShows />);

        const combobox = screen.getByRole("combobox");

        await act(async () => {
            fireEvent.mouseDown(combobox);
        });

        const options = screen.getByRole("listbox");
        expect(options).toBeInTheDocument();
        expect(options.innerHTML).not.toContain("Doctor Who");
        expect(options.innerHTML).not.toContain("Maigret");
    });

    it("should subscribe the user to the search when the form is submitted", async () => {
        render(<SubscriptionFormWithShows />);
        
        const combobox = screen.getByRole("combobox");

        await act(async () => {
            fireEvent.mouseDown(combobox);
            fireEvent.change(combobox, { target: { value: "The Crown" } });
        });

        const submitButton = screen.getByRole("button", { name: "Submit" });

        await act(async () => {
            fireEvent.click(submitButton);
        });

        expect(mockUpdateSubscriptions).toHaveBeenCalled();
        // https://stackoverflow.com/questions/75485659/mock-antd-form-hook-using-react-testing-library
        // requires React 18 to update @testing-library/react to have renderHook to test what 
        // mockUpdateSubscriptions has been called with
        expect(mockToggleModal).toHaveBeenCalled();
    });
});