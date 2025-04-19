
import { deleteRequest, getRequest, postRequest, putRequest } from "./api-client";
import { Reminder, ReminderFormValues } from "../utils/types";

export const getReminders = async () => {
    const reminders = await getRequest<Reminder[]>("/reminders");
    return reminders;
};

export const addReminder = async (reminder: ReminderFormValues, token: string) => {
    return await postRequest<ReminderFormValues, Reminder>(
        `/reminders`,
        reminder,
        { Authorization: `Bearer ${token}` }
    );
};

export const editReminder = async (reminderDetails: ReminderFormValues, token: string) => {
    return await putRequest<ReminderFormValues, Reminder>(
        `/reminder/${reminderDetails.show}`,
        reminderDetails,
        { Authorization: `Bearer ${token}` }
    );
};

export const deleteReminder = async (show: string, token: string) => {
    return await deleteRequest(`/reminder/${show}`, { Authorization: `Bearer ${token}` });
};
