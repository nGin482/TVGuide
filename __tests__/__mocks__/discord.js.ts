import { Message, Snowflake, TextChannel, User } from "discord.js";

const mockLogin = jest.fn().mockResolvedValue("MOCK_TOKEN");
const mockOn = jest.fn();
const mockOnce = jest.fn();
export const mockGetChannels = jest.fn<TextChannel | undefined, [id: Snowflake]>();
export const mockGetUsers = jest.fn<User | undefined, [id: Snowflake]>();
export const mockSend = jest.fn<Message, [id: Snowflake]>();

interface MockChannelOptions {
  id?: string | Snowflake;
  name?: string;
  topic?: string;
  [key: string]: any; // Allows custom methods or spies
}

export interface MockUserOptions {
  id?: string | Snowflake;
  username?: string;
  [key: string]: any;
}

export function createMockUser(overrides: MockUserOptions = {}): User {
  const mockUser = {
    id: "888888888888888888" as Snowflake,
    username: "nGin",
    send: mockSend,
    ...overrides,
  };

  return mockUser as unknown as User;
}

export function createMockTextChannel(
  overrides: MockChannelOptions = {}
): TextChannel {
  const mockChannel = {
    id: "123456789012345678" as Snowflake,
    name: "general",
    type: ChannelType.GuildText,
    isTextBased: jest.fn().mockReturnValue(true),
    isThread: jest.fn().mockReturnValue(false),
    
    send: mockSend,
    bulkDelete: jest.fn().mockResolvedValue(new Map()),
    
    ...overrides,
  };

  return mockChannel as unknown as TextChannel;
}


export class Client {
  login = mockLogin;
  on = mockOn;
  once = mockOnce;
  channels = {
    cache: {
      get: mockGetChannels,
    },
  };
  users = {
    cache: {
      get: mockGetUsers,
    },
  };

  constructor() {}
}


export const GatewayIntentBits = {
  Guilds: 1 << 0,
  GuildMessages: 1 << 9,
  MessageContent: 1 << 15,
};

export const ActivityType = {
  Watching: 3,
  Playing: 0,
};

export enum ChannelType {
  GuildText = 0,
};