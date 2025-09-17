"use client"

import type React from "react"

import { useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Paperclip } from "lucide-react"
import { mockChatMessages, type ChatMessage } from "@/lib/mock-data"
import { useAuthStore } from "@/lib/store"
import { Link } from "lucide-react"
export default function TicketIntakePage() {
  const { user } = useAuthStore()
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages)
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      message: inputMessage,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage("")
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        message: getAIResponse(inputMessage),
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiResponse])
      setIsLoading(false)
    }, 1500)
  }

  const getAIResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase()

    if (lowerMessage.includes("invoice") || lowerMessage.includes("payment")) {
      return "I understand you're having an issue with invoices or payments. Can you please provide more details about:\n\n1. The specific error message you're seeing\n2. The invoice number or vendor name\n3. When did this issue first occur?\n\nThis will help me create a proper ticket for the finance team."
    }

    if (lowerMessage.includes("slow") || lowerMessage.includes("performance")) {
      return "I see you're experiencing performance issues. To help diagnose this better, could you tell me:\n\n1. Which system or application is running slowly?\n2. How long have you been experiencing this?\n3. Are other users in your department affected?\n\nI'll also need to gather some technical details to escalate this properly."
    }

    if (lowerMessage.includes("access") || lowerMessage.includes("login")) {
      return "I can help you with access issues. Please provide:\n\n1. Which system you're trying to access\n2. Your employee ID\n3. Any error messages you're seeing\n\nI'll create a ticket for the IT team to resolve your access issue quickly."
    }

    return "Thank you for providing that information. Let me ask a few follow-up questions to ensure I capture all the necessary details for your ticket:\n\n1. What is the business impact of this issue?\n2. How urgent is this for your work?\n3. Have you tried any troubleshooting steps?\n\nOnce I have these details, I'll create a ticket and provide you with a reference number."
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto">
        <Card className="h-[calc(100vh-12rem)]">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="flex items-center space-x-2">
                <span>AI Support Assistant</span>
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
              </CardTitle>
              <Link href="/create-ticket">
                <Button variant="outline" size="sm">Switch to Form</Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent className="flex flex-col h-full p-0">
            <ScrollArea className="flex-1 p-6">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className={`chat-message ${message.sender}`}>
                    <div className={`chat-bubble ${message.sender}`}>
                      <p className="whitespace-pre-line">{message.message}</p>
                      <p className="text-xs opacity-70 mt-1">{new Date(message.timestamp).toLocaleTimeString()}</p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="chat-message ai">
                    <div className="chat-bubble ai">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-current rounded-full animate-bounce" />
                        <div
                          className="w-2 h-2 bg-current rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        />
                        <div
                          className="w-2 h-2 bg-current rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            <div className="border-t p-4">
              <div className="flex space-x-2">
                <Button variant="outline" size="icon">
                  <Paperclip className="h-4 w-4" />
                </Button>
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Describe your issue..."
                  className="flex-1"
                  disabled={isLoading}
                />
                <Button onClick={handleSendMessage} disabled={!inputMessage.trim() || isLoading}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
