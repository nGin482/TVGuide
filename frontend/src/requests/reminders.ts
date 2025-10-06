
import { deleteRequest, getRequest, postRequest, putRequest } from "./api-client";
import { Reminder, ReminderFormValues } from "../utils/types";

export const getReminders = async () => {
    const reminders = await getRequest<Reminder[]>("/reminders");
    return reminders;
};

export const addReminder = async (reminder: ReminderFormValues) => {
    return await postRequest<ReminderFormValues, Reminder>(`/reminders`, reminder);
};

export const editReminder = async (reminderDetails: ReminderFormValues) => {
    return await putRequest<ReminderFormValues, Reminder>(
        `/reminder/${reminderDetails.show}`,
        reminderDetails
    );
};

export const deleteReminder = async (show: string) => {
    return await deleteRequest(`/reminder/${show}`);
};
