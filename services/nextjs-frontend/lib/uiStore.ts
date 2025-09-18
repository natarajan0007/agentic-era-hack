import { create } from 'zustand';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

interface UIStore {
  isChatMinimized: boolean;
  toggleChatMinimize: () => void;
  messages: Message[];
  addMessage: (message: Message) => void;
  updateLastMessage: (text: string) => void;
  clearChat: () => void;
}

export const useUIStore = create<UIStore>((set, get) => ({
  isChatMinimized: false,
  toggleChatMinimize: () => set((state) => ({ isChatMinimized: !state.isChatMinimized })),
  messages: [],
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  updateLastMessage: (text) => {
    const messages = get().messages;
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.sender === 'bot') {
        const newMessages = [...messages];
        newMessages[newMessages.length - 1] = { ...lastMessage, text };
        set({ messages: newMessages });
      }
    }
  },
  clearChat: () => set({ messages: [] }),
}));
