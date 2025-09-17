"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { mockTickets, mockMetrics } from "@/lib/mock-data"
import { Clock, CheckCircle, AlertCircle, TrendingUp } from "lucide-react"
import Link from "next/link"
import { AIAssistantPanel } from "@/components/ai-assistant-panel"

export default function L1DashboardPage() {
  const assignedTickets = mockTickets.filter(
    (ticket) => ticket.assignedTo === "l1@intellica.com" && ["open", "in-progress"].includes(ticket.status),
  )

  const recentlyClosed = mockTickets.filter(
    (ticket) => ticket.assignedTo === "l1@intellica.com" && ticket.status === "resolved",
  )

  const metrics = mockMetrics.l1

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">L1 Support Dashboard</h1>
          <p className="text-muted-foreground">Monitor your tickets and performance metrics</p>
        </div>

        {/* Metrics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tickets Resolved Today</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.ticketsResolvedToday}</div>
              <p className="text-xs text-muted-foreground">+2 from yesterday</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Resolution Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.averageResolutionTime}</div>
              <p className="text-xs text-muted-foreground">-0.3h from last week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">CSAT Score</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.csatScore}/5</div>
              <p className="text-xs text-muted-foreground">+0.2 from last month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">SLA Compliance</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.slaCompliance}%</div>
              <p className="text-xs text-muted-foreground">Target: 95%</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Assigned Tickets */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Assigned to Me</CardTitle>
                <CardDescription>Tickets currently assigned to you</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {assignedTickets.map((ticket) => (
                    <div key={ticket.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <Link href={`/tickets/${ticket.id}`} className="font-medium hover:underline">
                            {ticket.title}
                          </Link>
                          <Badge variant={ticket.priority === "high" ? "destructive" : "secondary"}>
                            {ticket.priority}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {ticket.id} • {ticket.department}
                        </p>
                        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          <span>SLA: {new Date(ticket.slaDeadline).toLocaleString()}</span>
                        </div>
                      </div>
                      <Badge variant={ticket.status === "in-progress" ? "default" : "outline"}>{ticket.status}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recently Closed</CardTitle>
                <CardDescription>Your recently resolved tickets</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentlyClosed.map((ticket) => (
                    <div key={ticket.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <Link href={`/tickets/${ticket.id}`} className="font-medium hover:underline">
                            {ticket.title}
                          </Link>
                          <Badge variant="outline">resolved</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {ticket.id} • Resolved on {new Date(ticket.updatedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AI Assistant Panel */}
          <div>
            <AIAssistantPanel userRole="l1-engineer" />
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
