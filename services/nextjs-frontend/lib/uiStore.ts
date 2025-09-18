import { create } from 'zustand';

interface Message {
  text: string;
  sender: 'user' | 'bot';
  files?: any[];
}

interface UIStore {
  isChatMinimized: boolean;
  toggleChatMinimize: () => void;
  messages: { [userId: string]: Message[] };
  addMessage: (userId: string, message: Message) => void;
  updateLastMessage: (userId: string, text: string) => void;
  clearChat: (userId: string) => void;
}

export const useUIStore = create<UIStore>((set, get) => ({
  isChatMinimized: false,
  toggleChatMinimize: () => set((state) => ({ isChatMinimized: !state.isChatMinimized })),
  messages: {},
  addMessage: (userId, message) => {
    const userMessages = get().messages[userId] || [];
    set((state) => ({
      messages: {
        ...state.messages,
        [userId]: [...userMessages, message],
      },
    }));
  },
  updateLastMessage: (userId, text) => {
    const userMessages = get().messages[userId];
    if (userMessages && userMessages.length > 0) {
      const lastMessage = userMessages[userMessages.length - 1];
      if (lastMessage.sender === 'bot') {
        const newMessages = [...userMessages];
        newMessages[newMessages.length - 1] = { ...lastMessage, text };
        set((state) => ({
          messages: {
            ...state.messages,
            [userId]: newMessages,
          },
        }));
      }
    }
  },
  clearChat: (userId) => {
    set((state) => ({
      messages: {
        ...state.messages,
        [userId]: [],
      },
    }));
  },
}));