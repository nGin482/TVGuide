import { fireEvent, render, screen } from '@testing-library/react';

import TVGuide from '../src/components/TVGuide';

import { currentUser, guide } from './test_data';

describe('test TVGuide component', () => {
    test('renders service buttons', () => {
        render(<TVGuide guide={guide} />);
        const ftaButton = screen.getByText(/Free to Air/i);
        const bbcButton = screen.getByText(/BBC Channels/i);
        const allButton = screen.getByText(/All/i);
        expect(ftaButton).toBeInTheDocument();
        expect(bbcButton).toBeInTheDocument();
        expect(allButton).toBeInTheDocument();
    });

    test('fta button only shows FTA guide', () => {
        render(<TVGuide guide={guide} />);
        const ftaButton = screen.getByText(/Free to Air/i);
        
        fireEvent.click(ftaButton);

        const maigret = screen.getByText(/^Maigret$/i);
        const deathInParadise = screen.queryByText(/Death in Paradise/i);
        expect(maigret).toBeInTheDocument();
        expect(deathInParadise).not.toBeInTheDocument();
    });

    test('bbc button only shows BBC guide', () => {
        render(<TVGuide guide={guide} />);
        const bbcButton = screen.getByText(/BBC Channels/i);
        
        fireEvent.click(bbcButton);

        const maigret = screen.queryByText(/^Maigret$/i);
        const deathInParadise = screen.queryByText(/Death in Paradise/i);
        expect(maigret).not.toBeInTheDocument();
        expect(deathInParadise).toBeInTheDocument();
    });

    test('all button shows FTA shows and BBC shows', () => {
        render(<TVGuide guide={guide} />);
        const allButton = screen.getByText(/All/i);

        fireEvent.click(allButton);

        const maigret = screen.queryByText(/^Maigret$/i);
        const deathInParadise = screen.queryByText(/Death in Paradise/i);
        expect(maigret).toBeInTheDocument();
        expect(deathInParadise).toBeInTheDocument();
    });

    test('TVGuide only renders shows user has sbscribed to', () => {
        render(<TVGuide guide={guide} user={currentUser} />);

        const maigret = screen.queryAllByText(/Maigret/i);
        const deathInParadise = screen.queryByText(/Death in Paradise/i);
        const vera = screen.queryByText(/Vera/i);
        const lewis = screen.queryByText(/Lewis/i);

        expect(maigret[0]).toBeInTheDocument();
        expect(deathInParadise).not.toBeInTheDocument();
        expect(vera).not.toBeInTheDocument();
        expect(lewis).not.toBeInTheDocument();
    })
});
