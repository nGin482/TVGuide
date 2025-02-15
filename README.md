# TVGuide

Repository for the TVGuide application created in python.
The application retrieves the data from the TV guide available on the ABC website, as well as the one on BBC Australia, and searches through the day's schedule to find a match from a given list of shows.
If one is found, the following information is collected:
  - The show scheduled
  - The time the show is on
  - The channel it is shown on
  - Any available episode information


## Environment Variables
- `HERMES`: The token to connect to the Discord bot
- `TVGUIDE_CHANNEL`: The id for the TVGuide channel (used for production)
- `DEV_CHANNEL`: The id for the development channel (used during development)
- `NGIN`: The user id to send direct messages (used for production)

- `PYTHON_ENV`: The runtime environment
- `TVGUIDE_DB`: The connection string to connect to MongoDB Atlas     `Deprecated`
- `LOCAL_DB`: The connection string for the development database      `Deprecated`
- `JWT_SECRET`: The JWT secret for the Flask API

- `DB_URL`: The Postgres database to connect to
- `VITE_BASE_URL`: The base URL used for sending API calls to the Flask API


## Running the TVGuide Locally
Running the TVGuide locally can be done by running the `local_guide.py` file.
The following arguments can be passed when running `local_guide.py`:
  - `--local-db`                //  runs a local version of the TVGuide using the local database
    - `--no-discord`            //  runs the TVGuide without using Discord - the guide will be printed to the console
    - `--import`                //  adds data to the local database
  - `--revert_tvguide`          //  revert the tvguide database to a previous state
If the `--local-db` argument is provided, MongoDB will need to be running locally first before running `local_guide.py`. See Local Database below for details
If no arguments are passed when running `local_guide.py`, the `development` database in MongoDB Atlas will be used.

When the TVGuide is run using Discord, the `development` channel will be used (as specified by the `DEV_CHANNEL` environment variable).

### Running the Flask API
In the root directory, run:
```
- python api.py
```

### Running the frontend
Ensure the FLask API is running
In a separate terminal, run:
```
- cd ./frontend
- npm start
```

## Local Database
- Create a local Postgres database
- Add the connection string to your .env file


### Deprecated
To use the local database, you will need to have MongoDB installed locally.
Version 7.0 of the Community Edition has been used in setting up the development environment.
MongoDB Compass can also be optionally installed.

To run the local database, first start the server by running: `mongod --dbpath="C:\Users\nicho\OneDrive\Desktop\PycharmProjects\TVGuide\dev-data\mongo_data"`.
It may be beneficial to add the `C:\Program Files\MongoDB\Server\7.0\bin\` folder where MongoDB was installed to the PATH variable, if this has not already been done.
Adding the `--db-path` argument tells MongoDB where to store the data on disk. This currently points to `./dev-data/mongo_data`.