import dayjs from "dayjs";

export const convertDate = (date: Date) => {
  const localTime = dayjs.tz(date, "Australia/Sydney");

  return dayjs.utc(localTime.format('YYYY-MM-DD HH:mm:ss')).toDate();
};
