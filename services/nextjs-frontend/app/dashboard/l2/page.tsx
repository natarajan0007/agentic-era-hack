"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { getTickets, getDashboardMetrics } from "@/lib/api"
import { Ticket } from "@/lib/mock-data"
import { Clock, CheckCircle, AlertCircle, TrendingUp } from "lucide-react"
import Link from "next/link"
import { AIAssistantPanel } from "@/components/ai-assistant-panel"
import { useAuthStore } from "@/lib/store"
import { useEffect, useState } from "react"

export default function L2DashboardPage() {
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
    (ticket) =>
      ticket.assignedTo === user?.email && ["open", "in-progress", "escalated"].includes(ticket.status),
  )

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">L2 Technical Specialist Dashboard</h1>
          <p className="text-muted-foreground">Monitor complex tickets and technical performance metrics</p>
        </div>

        {/* Metrics Cards */}
        {loading || !metrics ? (
          <p>Loading metrics...</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Escalated Tickets Resolved</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.resolved_tickets}</div>
                <p className="text-xs text-muted-foreground">+1 from yesterday</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">RCA Completion Rate</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">80%</div>
                <p className="text-xs text-muted-foreground">+5% from last week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Complex Issues Resolved</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.resolved_tickets}</div>
                <p className="text-xs text-muted-foreground">+1 from last week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Resolution Time</CardTitle>
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.avg_resolution_time}</div>
                <p className="text-xs text-muted-foreground">Target: 4 hours</p>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Assigned Tickets */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Assigned Complex Tickets</CardTitle>
                <CardDescription>Technical issues requiring specialist attention</CardDescription>
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
                        <Badge variant={ticket.status === "escalated" ? "destructive" : "default"}>{ticket.status}</Badge>
                      </div>
                    ))}
                    {assignedTickets.length === 0 && (
                      <div className="text-center py-6 text-muted-foreground">No tickets currently assigned to you</div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Knowledge Articles Created</CardTitle>
                <CardDescription>Recent technical documentation you've contributed</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <Link href="/knowledge/article-1" className="font-medium hover:underline">
                        Resolving Database Connection Pool Issues in P2P System
                      </Link>
                      <p className="text-sm text-muted-foreground">Created 2 days ago</p>
                    </div>
                    <Badge variant="outline">Technical</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <Link href="/knowledge/article-2" className="font-medium hover:underline">
                        Optimizing Query Performance for Invoice Matching
                      </Link>
                      <p className="text-sm text-muted-foreground">Created 5 days ago</p>
                    </div>
                    <Badge variant="outline">Performance</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AI Assistant Panel */}
          <div>
            <AIAssistantPanel userRole="l2-engineer" />
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
