import { render, screen } from '@testing-library/react';

import TVGuide from '../src/components/TVGuide';
import { Guide } from '../src/utils/types';

import { currentUser, guide } from './test_data';
import dayjs from 'dayjs';

describe("Test TVGuide component", () => {
    test("TVGuide only renders shows user has subscribed to", () => {
        render(<TVGuide guide={guide} user={currentUser} />);

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
        const currentTime = new Date();
        const ftaData = guide.fta.map((show, idx) => {
            if (idx === 1) {
                show.start_time = `${currentTime.getHours()}:${currentTime.getMinutes()}`;
                show.end_time = `${currentTime.getHours() + 2}:${currentTime.getMinutes()}`;
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
        const currentTime = new Date();
        const ftaData = guide.fta.map((show, idx) => {
            if (idx === 0) {
                show.start_time = `${currentTime.getHours() - 2}:${currentTime.getMinutes()}`;
                show.end_time = `${currentTime.getHours() - 1}:${currentTime.getMinutes()}`;
            }
            return show;
        });
        const guideData: Guide = {
            fta: ftaData,
            bbc: [],
        };

        render(<TVGuide guide={guideData} />);

        const rows = screen.getAllByRole("row");
        expect(rows[1]).toHaveClass("finished")
    });
});
