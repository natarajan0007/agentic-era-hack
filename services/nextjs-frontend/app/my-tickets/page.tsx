"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { getTickets, getDashboardMetrics } from "@/lib/api"
import { Ticket } from "@/lib/mock-data"
import { Clock, CheckCircle, AlertCircle, TrendingUp, Ticket as TicketIcon, CircleDot, Loader, CheckCircle2, ArrowUpCircle } from "lucide-react"
import Link from "next/link"
import { ChatPanel } from "@/components/chat-panel"
import { useAuthStore } from "@/lib/store"
import { useEffect, useState } from "react"

export default function MyTicketsPage() {
  const { user } = useAuthStore()
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      const [fetchedTickets, fetchedMetrics] = await Promise.all([
        getTickets(),
        getDashboardMetrics(),
      ])
      setTickets(fetchedTickets)
      setMetrics(fetchedMetrics)
      setLoading(false)
    }

    fetchData()
  }, [])

  const assignedTickets = tickets.filter(
    (ticket) => ticket.assignee?.email === user?.email && ["OPEN", "IN_PROGRESS"].includes(ticket.status),
  )

  const recentlyClosed = tickets.filter(
    (ticket) => ticket.assignee?.email === user?.email && ticket.status === "RESOLVED",
  )

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Tickets</h1>
          <p className="text-muted-foreground">Monitor your tickets and performance metrics</p>
        </div>

        {/* Metrics Cards */}
        {loading || !metrics ? (
          <p>Loading metrics...</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Tickets</CardTitle>
                <TicketIcon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.total_tickets}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tickets In Progress</CardTitle>
                <Loader className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.in_progress_tickets}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tickets Resolved Today</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.resolved_tickets}</div>
                <p className="text-xs text-muted-foreground">+2 from yesterday</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Resolution Time</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.avg_resolution_time} hours</div>
                <p className="text-xs text-muted-foreground">-0.3h from last week</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">CSAT Score</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">4.2/5</div>
                <p className="text-xs text-muted-foreground">+0.2 from last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">SLA Compliance</CardTitle>
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.sla_compliance_rate}%</div>
                <p className="text-xs text-muted-foreground">Target: 95%</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Escalated Tickets</CardTitle>
                <ArrowUpCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.escalated_tickets}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Closed Tickets</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.closed_tickets}</div>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Assigned Tickets */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Assigned to Me</CardTitle>
                <CardDescription>Tickets currently assigned to you</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading tickets...</p>
                ) : (
                  <div className="space-y-4">
                    {assignedTickets.map((ticket) => (
                      <div key={ticket.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <Link href={`/tickets/${ticket.id}`} className="font-medium hover:underline">
                              {ticket.title}
                            </Link>
                            <Badge variant={ticket.priority === "HIGH" ? "destructive" : "secondary"}>
                              {ticket.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {ticket.id} • {ticket.department.name}
                          </p>
                          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            <span>SLA: {new Date(ticket.sla_deadline).toLocaleString()}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Link href={`/tickets/${ticket.id}`}>
                            <Button variant="outline" size="sm">View</Button>
                          </Link>
                          <Badge variant={ticket.status === "IN_PROGRESS" ? "default" : "outline"}>{ticket.status}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recently Closed</CardTitle>
                <CardDescription>Your recently resolved tickets</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading tickets...</p>
                ) : (
                  <div className="space-y-4">
                    {recentlyClosed.map((ticket) => (
                      <div key={ticket.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <Link href={`/tickets/${ticket.id}`} className="font-medium hover:underline">
                              {ticket.title}
                            </Link>
                            <div className="flex items-center space-x-2">
                          <Link href={`/tickets/${ticket.id}`}>
                            <Button variant="outline" size="sm">View</Button>
                          </Link>
                          <Badge variant="outline">RESOLVED</Badge>
                        </div>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {ticket.id} • Resolved on {new Date(ticket.updatedAt).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* AI Assistant Panel */}
          <div>
            <ChatPanel />
          </div>
        </div>
      </div>
    </AppLayout>
  )
}