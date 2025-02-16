import axios, { AxiosResponse } from "axios";

import {
    addReminder,
    addNewShow,
    changePassword,
    deleteReminder,
    editReminder,
    getGuide,
    getShows,
    getReminders,
    getUser,
    login,
    registerNewUser,
    removeShowFromList,
    addSubscriptions
} from "../src/requests";
import {
    addSearchItem,
    guide,
    loginRes,
    newShowPayload,
    newUser,
    newUserRes,
    shows,
    reminders,
    searchList,
    updateSubscriptionsRes,
    user
} from "./test_data";
import { AccountDetailsFormValues, Reminder } from "../src/utils/types";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

const response: AxiosResponse = {
    status: 200,
    statusText: 'OK',
    data: null,
    headers: null,
    config: null
};

const badResponse: AxiosResponse = {
    status: 404,
    statusText: 'Not Found',
    data: null,
    headers: null,
    config: null
};

describe("Fetch Guide data", () => {
    test('returns 200 when retrieving guide', async () => {
        
        response.data = guide;
        
        mockedAxios.get.mockResolvedValue(response);
        const guideRes = await getGuide();
        expect(guideRes.fta[0].title).toEqual(guide.fta[0].title);
    });
    
    // fail condition
    test('throws an error when unable to retrieve TV guide', async () => {
        mockedAxios.get.mockRejectedValue(Error(`${badResponse.status} ${badResponse.statusText}`));
        expect(async () => await getGuide()).rejects.toThrow(`${badResponse.status} ${badResponse.statusText}`);
    });
});

describe("Handling Show Data", () => {
    test("should successfully retrive data for all shows", async () => {

        response.data = shows;
        
        mockedAxios.get.mockResolvedValue(response);
        const searchListResponse = await getShows();
        expect(searchListResponse[0].show_name).toEqual(searchList[0].show);
    });

    test.skip('throws an error when unable to retrieve SearchList', async () => {
        mockedAxios.get.mockRejectedValue(Error(`${badResponse.status} ${badResponse.statusText}`));
        await expect(async () => await getGuide()).rejects.toThrow(`${badResponse.status} ${badResponse.statusText}`);
    });

    test("creates a new show and returns the created details", async () => {
        response.data = addSearchItem;

        mockedAxios.post.mockResolvedValue(response);
        const newShowData = await addNewShow(newShowPayload, 'test-token');
        
        expect(newShowData).toEqual(addSearchItem);
    });

    test.skip('returns error when unable to add searchItem', async () => {
        mockedAxios.post.mockRejectedValue(Error(`${badResponse.status} ${badResponse.statusText}`));

        await expect(async () => await addNewShow(newShowPayload, 'test-token')).rejects.toMatchObject(badResponse);
    });

    test.skip('returns updated searchList when searchItem deleted', async () => {
        await removeShowFromList(addSearchItem.show, 'test-token');
        
        // expect(res.result).toEqual('success');
        // let payload: SearchItemResponses;
        // if (res.result === 'success') {
        //     payload = res.payload;
        // }
        // expect(payload.searchList.length).toBeLessThan(addSearchItemResponse.searchList.length);
    });

    test("successfully retrieves all Reminders", async () => {
        response.data = reminders;

        mockedAxios.get.mockResolvedValue(response);
        const res = await getReminders();
        
        expect(res.length).toBeGreaterThan(0);
        expect(res[0].show).toEqual(reminders[0].show);
    });

    test("should be able to create a Reminder", async () => {
        const newReminder: Reminder = {
            show: 'Endeavour',
            warning_time: 5,
            alert: 'Before',
            occasions: 'All'
        };
        response.data = newReminder;

        mockedAxios.post.mockResolvedValue(response);
        const res = await addReminder(newReminder, 'test-token');

        expect(res.show).toContain(newReminder.show);
    });

    test("is able to edit a Reminder", async () => {
        const editReminderPayload: Reminder = {
            show: 'Doctor Who',
            warning_time: 3,
            alert: 'Before',
            occasions: 'All'
        };
        const updatedReminder = reminders.find(remidner => remidner.show === "Doctor Who");
        updatedReminder.warning_time = 3;
        response.data = updatedReminder;

        mockedAxios.put.mockResolvedValue(response);
        const res = await editReminder(editReminderPayload, 'test-token');

        expect(res.warning_time).toEqual(3);
    });

    test.skip('is able to delete a Reminder', async () => {
        response.data = {
            result: 'success',
            reminders: reminders.filter(reminder => reminder.show !== 'Maigret')
        };

        mockedAxios.delete.mockResolvedValue(response);
        const res = await deleteReminder('Maigret', 'test-token');

        // let length = res.payload.reminders.length;
        // expect(length).toBeLessThan(reminders.length);
        // let maigretFound = false;
        // res.payload.reminders.forEach(reminder => {
        //     if (reminder.show === 'Maigret') {
        //         maigretFound = true;
        //     }
        // });
        // expect(maigretFound).toBe(false);
    });
});

describe("Handle User Data", () => {
    test("is able to retrieve a user", async () => {
        response.data = user;

        mockedAxios.get.mockResolvedValue(response);
        const res = await getUser('Test');

        expect(res.username).toEqual(user.username);
    });

    test("is able to register a new user", async () => {
        response.data = newUserRes;

        mockedAxios.post.mockResolvedValue(response);
        const userResponse = await registerNewUser(newUser);

        expect(userResponse.username).toEqual(newUserRes.username);
        expect(userResponse.show_subscriptions).toEqual(newUserRes.show_subscriptions);
    });

    test("is able to update password of user", async () => {
        response.data = { ...user, password: 'updated-password' };
        mockedAxios.post.mockResolvedValue(response);

        const updatedAccountDetails: AccountDetailsFormValues = {
            password: "updated-password"
        };

        const userResponse = await changePassword('Test', updatedAccountDetails, 'test-token');
        expect(Object.values(userResponse)).toContain("updated-password");
    });

    test("is able to add to a user's subscriptions", async () => {
        response.data = updateSubscriptionsRes

        mockedAxios.put.mockResolvedValue(response);
        const userResponse = await addSubscriptions('Test', ['Vera'], 'test-token');

       const latestSubscription = userResponse.show_subscriptions[userResponse.show_subscriptions.length - 1];
        expect(userResponse.show_subscriptions.length).toBeGreaterThan(user.show_subscriptions.length);
        expect(latestSubscription.search_item.show).toContain('Vera');
    });

    test("is able to log a user in", async () => {
        response.data = loginRes;

        mockedAxios.post.mockResolvedValue(response);
        const userResponse = await login({ username: 'Test', password: 'password' });

        expect(userResponse.username).toEqual('Test');
        expect(userResponse.token).toEqual("test-token");
    });
});