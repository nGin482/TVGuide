# TVGuide

Repository for the TVGuide application created in python.
The application retrieves the data from the TV guide available on the ABC website, as well as the one on BBC Australia, and searches through the day's schedule to find a match from a given list of shows.
If one is found, the following information is collected:
  - The show scheduled
  - The time the show is on
  - The channel it is shown on
  - Any available episode information

## List of Shows
  - Vera
  - Endeavour
  - Lewis
  - Maigret
  - Unforgotten
  - Death in Paradise
  - Shetland
  - NCIS
  - NCIS: Los Angeles
  - Mock The Week
  - No Offence
  - Mad As Hell
  - Grantchester
  - Doctor Who
  - Transformers
  - Inspector Morse
  - Baptiste

## To Do List
1. Reorganise how the show listings are collected and stored
  - See if the repeat handler can be improved
  - When the requests are made and the information gathered, the data will be stored in a JSON file /similar/ to those in backups - for the current day
  - This JSON file will be used by the reminders and once the requests are made again, the current JSON file will be moved to /backups
2. Set reminders
3. Deploy