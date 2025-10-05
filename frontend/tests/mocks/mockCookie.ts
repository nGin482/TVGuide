export const mockGetCookie = jest.fn();
export const mockSetCookie = jest.fn();
export const mockRemoveCookie = jest.fn();

export class MockCookies {
    get = mockGetCookie;
    set = mockSetCookie;
    remove = mockRemoveCookie;
}


