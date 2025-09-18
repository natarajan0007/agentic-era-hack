"use client";
import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, User, Bot, Trash2, Minus, Paperclip } from 'lucide-react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { createChatSession } from '@/lib/api';
import { useUIStore } from '@/lib/uiStore';
import { useAuthStore } from '@/lib/store';
import { formatUserName } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';

interface Message {
  text: string;
  sender: 'user' | 'bot';
  files?: any[];
}

export function ChatPanel() {
  const { user } = useAuthStore();
  const userId = user?.email || 'anonymous';
  const { isChatMinimized, toggleChatMinimize, messages, addMessage, updateLastMessage, clearChat } = useUIStore();
  const userMessages = messages[userId] || [];

  const userName = formatUserName(user?.email);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [files, setFiles] = useState<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initSession = async () => {
      const storedSessionId = localStorage.getItem(`chat_session_id_${userId}`);
      if (storedSessionId) {
        setSessionId(storedSessionId);
      } else if (user?.email) {
        try {
          const newSessionId = await createChatSession(user.email);
          localStorage.setItem(`chat_session_id_${userId}`, newSessionId);
          setSessionId(newSessionId);
        } catch (error) {
          console.error("Failed to create chat session:", error);
        }
      }
    };
    initSession();
  }, [user, userId]);

  const handleClearChat = async () => {
    console.log('Clearing chat and creating new session');
    clearChat(userId);
    localStorage.removeItem(`chat_session_id_${userId}`);
    if (user?.email) {
      try {
        console.log('Creating new session for user:', user.email);
        const newSessionId = await createChatSession(user.email);
        console.log('New session created after clear:', newSessionId);
        setSessionId(newSessionId);
        localStorage.setItem(`chat_session_id_${userId}`, newSessionId);
      } catch (error) {
        console.error("Failed to create new chat session:", error);
        setSessionId(null);
      }
    } else {
      console.log('No user email, setting session to null');
      setSessionId(null);
    setFiles([]);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (selectedFiles) {
      const newFiles = Array.from(selectedFiles).map(file => {
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => {
            resolve({
              name: file.name,
              type: file.type,
              data: (reader.result as string).split(',')[1],
            });
          };
          reader.onerror = reject;
          reader.readAsDataURL(file);
        });
      });
      Promise.all(newFiles).then(processedFiles => {
        setFiles(prevFiles => [...prevFiles, ...processedFiles]);
      });
    }
  };

  const handleSendMessage = async () => {
    const textToSend = input.trim();
    
    if (textToSend === '' && files.length === 0) {
      console.log('Cannot send message: empty text and no files');
      return;
    }

    if (!sessionId) {
      console.log('No session ID available, cannot send message');
      updateLastMessage(userId, '❌ No active session. Please refresh the page or click the trash icon to start a new session.');
      return;
    }

    const userMessage: Message = { text: textToSend, sender: 'user', files: files };
    addMessage(userId, userMessage);
    
    const botMessage: Message = { text: "Thinking...", sender: 'bot' };
    addMessage(userId, botMessage);
    
    setIsThinking(true);
    
    try {
      const adkUserId = user?.email ? user.email.replace(/[@.]/g, '_') : 'nat';
      
      const parts: any[] = [{ text: textToSend }];
      files.forEach(file => {
        parts.push({
          inlineData: {
            displayName: file.name,
            mimeType: file.type,
            data: file.data,
          }
        });
      });

      const requestBody = {
        appName: "AURA",
        userId: adkUserId,
        sessionId: sessionId,
        newMessage: {
          parts: parts,
          role: "user"
        },
        streaming: true
      };
      
      console.log('Sending request with payload:', JSON.stringify(requestBody, null, 2));
      console.log('Session ID being used:', sessionId);
      
      let fullResponse = '';
      const adkApiBaseUrl = process.env.NEXT_PUBLIC_ADK_API_URL || 'http://localhost:8010';
      const apiUrl = `${adkApiBaseUrl}/run_sse`;
      console.log('API URL:', apiUrl);
      
      await fetchEventSource(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(requestBody),
        onopen(response) {
          console.log('Connection opened:', response.status, response.statusText);
          if (response.ok) {
            updateLastMessage(userId, '');
            setInput('');
            setFiles([]);
            return;
          }
          setIsThinking(false);
          
          if (response.status === 404) {
            console.error('API endpoint not found - check if server is running and endpoint exists');
            throw new Error(`API endpoint not found (404). Check if the server is running at ${apiUrl}`);
          } else if (response.status === 400) {
            console.error('Bad request - check payload format');
            throw new Error(`Bad request (400). Invalid payload format.`);
          } else if (response.status === 500) {
            console.error('Server error');
            throw new Error(`Server error (500). Check server logs.`);
          }
          
          throw new Error(`Failed to connect: ${response.status} ${response.statusText}`);
        },
        onmessage(event) {
          console.log('Received message:', event.data);
          setIsThinking(false);
          try {
            const data = JSON.parse(event.data);
            console.log('Parsed data:', data);
            if (data.content && data.content.parts && data.content.parts[0].text) {
              if (data.partial) {
                fullResponse += data.content.parts[0].text;
              } else {
                fullResponse = data.content.parts[0].text;
              }
              updateLastMessage(userId, fullResponse);
            } else {
              console.log('Unexpected data format:', data);
            }
          } catch (parseError) {
            console.error('Error parsing message data:', parseError, 'Raw data:', event.data);
          }
        },
        onerror(err) {
          console.error('EventSource error:', err);
          setIsThinking(false);
          throw err;
        },
      });
    } catch (error) {
      console.error('Chat error:', error);
      setIsThinking(false);
      updateLastMessage(userId, `❌ ${error.message || 'Connection failed'} Click the trash icon to start a new session.`);
    }
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [userMessages]);

  return (
      <Card className="flex flex-col bg-background border rounded-lg shadow-sm w-full h-full">
        <CardHeader className="border-b p-3 drag-handle cursor-move bg-gray-800 dark:bg-gray-900 text-white flex-shrink-0">
          <CardTitle className="flex items-center justify-between gap-2 text-base">
            <div className="flex items-center gap-2">
              <motion.div
                animate={{
                  scale: isThinking ? 1.2 : 1,
                  y: isThinking ? [0, -5, 0] : [0, -2, 0],
                }}
                transition={{
                  duration: isThinking ? 0.5 : 1.5,
                  repeat: Infinity,
                  repeatType: "reverse",
                  ease: "easeInOut",
                }}
              >
                <Bot className="w-6 h-6 text-white" />
              </motion.div>
              <span className="text-gray-200">AURA Agentic AI Assistant</span>
            </div>
            <div className="flex items-center">
              <motion.div whileHover={{ scale: 1.1, rotate: 10 }}>
                <Button variant="ghost" size="icon" onClick={handleClearChat}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.1, rotate: 10 }}>
                <Button variant="ghost" size="icon" onClick={toggleChatMinimize}>
                  <Minus className="w-4 h-4" />
                </Button>
              </motion.div>
            </div>
          </CardTitle>
        </CardHeader>
        {!isChatMinimized && (
        <CardContent className="flex flex-col p-0 flex-1 min-h-0">
          <ScrollArea className="flex-1 p-3" ref={scrollAreaRef}>
            <div className="space-y-3">
              {userMessages.length === 0 ? (
                <div className="text-center text-sm text-muted-foreground p-3">
                  <p>Hello {userName}! How can I assist you today?</p>
                </div>
              ) : (
                userMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex items-start gap-2 ${message.sender === 'user' ? 'justify-end' : ''}`}
                  >
                    {message.sender === 'bot' && (
                      <div className="flex items-center justify-center w-7 h-7 rounded-full bg-muted flex-shrink-0">
                        <Bot className="w-3 h-3" />
                      </div>
                    )}
                    <div
                      className={`max-w-[85%] p-2.5 text-sm rounded-lg prose prose-sm dark:prose-invert ${
                        message.sender === 'user'
                          ? 'bg-primary text-primary-foreground rounded-br-none'
                          : 'bg-muted rounded-bl-none'
                      }`}
                    >
                      <ReactMarkdown>{message.text}</ReactMarkdown>
                      {message.files && message.files.length > 0 && (
                        <div className="mt-2">
                          {message.files.map((file, index) => (
                            <div key={index}>
                              {file.type.startsWith('image/') ? (
                                <img
                                  src={`data:${file.type};base64,${file.data}`}
                                  alt={file.name}
                                  className="max-w-full h-auto rounded-lg"
                                />
                              ) : (
                                <a
                                  href={`data:${file.type};base64,${file.data}`}
                                  download={file.name}
                                  className="text-blue-500 underline"
                                >
                                  {file.name}
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    {message.sender === 'user' && (
                      <div className="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-primary-foreground flex-shrink-0">
                        <User className="w-3 h-3" />
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
          <div className="p-2 border-t flex-shrink-0">
            {files.length > 0 && (
              <div className="p-2 border-b">
                <p className="text-sm font-medium">Selected files:</p>
                <ul className="text-sm text-muted-foreground">
                  {files.map((file, index) => (
                    <li key={index}>{file.name}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="flex items-center gap-1.5">
              <Input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                multiple
                accept=".png,.jpeg,.jpg,.pdf,.txt"
                className="hidden"
              />
              <Button
                onClick={() => fileInputRef.current?.click()}
                variant="ghost"
                size="icon"
              >
                <Paperclip className="w-4 h-4" />
              </Button>
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your message..."
                className="flex-grow h-9 text-sm"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!input.trim() && files.length === 0}
                className="rounded-full w-8 h-8 p-0"
                size="sm"
              >
                <Send className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        </CardContent>
        )}
      </Card>
  );
}