"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Bot } from "lucide-react"

interface AIAssistantPanelProps {
  userRole: string
  ticketId?: string
}

interface Message {
  id: string
  sender: "user" | "ai"
  message: string
  timestamp: string
}

export function AIAssistantPanel({ userRole, ticketId }: AIAssistantPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "ai",
      message: `Hello! I'm your AI Smart Assistant. I can help you with ticket analysis, finding solutions, and accessing system information. How can I assist you today?`,
      timestamp: new Date().toISOString(),
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: Message = {
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
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        message: getAIResponse(inputMessage, userRole, ticketId),
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiResponse])
      setIsLoading(false)
    }, 1500)
  }

  const getAIResponse = (userMessage: string, role: string, ticketId?: string): string => {
    const lowerMessage = userMessage.toLowerCase()

    if (lowerMessage.includes("logs") || lowerMessage.includes("melt")) {
      return `I've retrieved the MELT data for ${ticketId || "the system"}:\n\n**Metrics:**\n- CPU Usage: 78% (elevated)\n- Memory: 6.2GB/8GB\n- Response Time: 12.4s (above normal)\n\n**Events:**\n- Database connection timeout at 10:45 AM\n- High query execution time detected\n\n**Logs:**\n- ERROR: Connection pool exhausted\n- WARN: Slow query detected (>10s)\n\n**Traces:**\n- Invoice matching process taking 12.4s\n- Database query bottleneck identified\n\nRecommendation: Check database connection pool settings and optimize slow queries.`
    }

    if (lowerMessage.includes("similar") || lowerMessage.includes("related")) {
      return `I found 3 similar tickets:\n\n1. **INC-20250601-045** - Invoice processing delays\n   - Resolution: Increased database connection pool\n   - Time to resolve: 2 hours\n\n2. **INC-20250528-123** - P2P system performance\n   - Resolution: Query optimization\n   - Time to resolve: 4 hours\n\n3. **INC-20250525-089** - ERP timeout errors\n   - Resolution: Server restart + config update\n   - Time to resolve: 1 hour\n\nWould you like me to show the detailed resolution steps for any of these?`
    }

    if (lowerMessage.includes("solution") || lowerMessage.includes("resolve")) {
      return `Based on the ticket analysis, here are the top 5 recommended solutions:\n\n**1. Database Connection Pool Optimization** (Automated)\n- Increase max connections from 50 to 100\n- Adjust timeout settings\n- Confidence: 85%\n\n**2. Query Performance Tuning** (Manual)\n- Identify and optimize slow queries\n- Add missing indexes\n- Confidence: 78%\n\n**3. Application Server Restart** (Automated)\n- Restart P2P application services\n- Clear cache and temporary files\n- Confidence: 65%\n\n**4. Load Balancer Configuration** (Manual)\n- Review traffic distribution\n- Adjust server weights\n- Confidence: 60%\n\n**5. System Resource Scaling** (Manual)\n- Consider increasing server resources\n- Monitor resource utilization\n- Confidence: 55%\n\nShall I execute the automated solutions or would you like more details on the manual steps?`
    }

    return `I understand you're asking about "${userMessage}". As your AI assistant, I can help you with:\n\n• Analyzing ticket data and logs\n• Finding similar incidents and solutions\n• Providing step-by-step resolution guidance\n• Accessing system metrics and traces\n• Suggesting automation opportunities\n\nCould you be more specific about what you'd like me to help you with?`
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <Card className="h-[600px]">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Bot className="h-5 w-5" />
          <span>AI Smart Assistant</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col h-full p-0">
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    message.sender === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                  }`}
                >
                  <p className="whitespace-pre-line text-sm">{message.message}</p>
                  <p className="text-xs opacity-70 mt-1">{new Date(message.timestamp).toLocaleTimeString()}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted p-3 rounded-lg">
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
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button onClick={handleSendMessage} disabled={!inputMessage.trim() || isLoading} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
