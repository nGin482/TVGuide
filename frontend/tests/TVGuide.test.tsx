import { render, screen } from '@testing-library/react';
import dayjs from 'dayjs';

import TVGuide from '../src/components/TVGuide';
import { Guide } from '../src/utils/types';

import { currentUser, guide } from './test_data';

describe("Test TVGuide component", () => {
    let guideCopy: Guide = JSON.parse(JSON.stringify(guide));

    beforeEach(() => {
        guideCopy = JSON.parse(JSON.stringify(guide));
    });

    test("TVGuide only renders shows user has subscribed to", () => {
        render(<TVGuide guide={guideCopy} user={currentUser} />);

        const maigret = screen.queryAllByText(/Maigret/i);
        const deathInParadise = screen.queryByText(/Death in Paradise/i);
        const vera = screen.queryByText(/Vera/i);
        const lewis = screen.queryByText(/Lewis/i);

        expect(maigret[0]).toBeInTheDocument();
        expect(deathInParadise).not.toBeInTheDocument();
        expect(vera).not.toBeInTheDocument();
        expect(lewis).not.toBeInTheDocument();
    });

    test("'airing' classname added to table row when show is airing", () => {
        const currentTime = dayjs();
        const ftaData = guideCopy.fta.map((show, idx) => {
            if (idx === 1) {
                show.start_time = `${currentTime.hour()}:${currentTime.minute()}`;
                show.end_time = `${currentTime.hour() + 2}:${currentTime.minute()}`;
            }
            return show;
        });
        const guideData: Guide = {
            fta: ftaData,
            bbc: [],
        };

        render(<TVGuide guide={guideData} />);

        screen.debug()
        const rows = screen.getAllByRole("row");
        console.log("rows", rows)
        expect(rows[1]).toHaveClass("airing")
    });

    test("'finished' classname added to table row when show has finished", () => {
        const currentTime = dayjs();
        const ftaData = guideCopy.fta.map((show, idx) => {
            if (idx === 0) {
                show.start_time = `${currentTime.hour() - 2}:${currentTime.minute()}`;
                show.end_time = `${currentTime.hour() - 1}:${currentTime.minute()}`;
            }
            return show;
        });
        const guideData: Guide = {
            fta: ftaData,
            bbc: [],
        };

        render(<TVGuide guide={guideData} />);

        screen.debug()
        const rows = screen.getAllByRole("row");
        expect(rows[1]).toHaveClass("finished")
    });
});
