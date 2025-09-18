"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { getTickets, getDashboardMetrics } from "@/lib/api"
import { Ticket } from "@/lib/mock-data"
import { Clock, Users, AlertCircle, TrendingUp, Filter } from "lucide-react"
import Link from "next/link"
import { ChatPanel } from "@/components/chat-panel"
import { useAuthStore } from "@/lib/store"
import { useEffect, useState } from "react"

export default function OpsManagerDashboardPage() {
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

  const criticalTickets = tickets.filter((ticket) => ticket.priority === "HIGH" || ticket.priority === "CRITICAL")

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Operations Manager Dashboard</h1>
          <p className="text-muted-foreground">Monitor team performance and ticket status</p>
        </div>

        {/* Metrics Cards */}
        {loading || !metrics ? (
          <p>Loading metrics...</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Active Tickets</CardTitle>
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.open_tickets}</div>
                <p className="text-xs text-muted-foreground">-3 from yesterday</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">L1 Team Performance</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">92%</div>
                <p className="text-xs text-muted-foreground">+2% from last week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">L2 Team Performance</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">88%</div>
                <p className="text-xs text-muted-foreground">+5% from last week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">SLA Compliance</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.sla_compliance}%</div>
                <p className="text-xs text-muted-foreground">Target: 95%</p>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Critical Tickets */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Critical Tickets</CardTitle>
                  <CardDescription>High priority issues requiring attention</CardDescription>
                </div>
                <Button variant="outline" size="sm" className="flex items-center gap-1">
                  <Filter className="h-4 w-4" />
                  Filter
                </Button>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p>Loading tickets...</p>
                ) : (
                  <div className="space-y-4">
                    {criticalTickets.map((ticket) => (
                      <div key={ticket.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <Link href={`/tickets/${ticket.id}`} className="font-medium hover:underline">
                              {ticket.title}
                            </Link>
                            <Badge variant="destructive">{ticket.priority}</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {ticket.id} • {ticket.department.name} • Assigned to:{" "}
                            {ticket.assignedTo?.split("@")[0] || "Unassigned"}
                          </p>
                          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            <span>SLA: {new Date(ticket.slaDeadline).toLocaleString()}</span>
                          </div>
                        </div>
                        <Badge variant={ticket.status === "OPEN" ? "destructive" : "default"}>{ticket.status}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Team Workload</CardTitle>
                <CardDescription>Current ticket distribution across team members</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <p className="font-medium">Sarah Wilson (L1)</p>
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div className="bg-primary h-2.5 rounded-full" style={{ width: "70%" }}></div>
                      </div>
                      <p className="text-sm text-muted-foreground">8 active tickets (70% capacity)</p>
                    </div>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <p className="font-medium">Mike Johnson (L2)</p>
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div className="bg-primary h-2.5 rounded-full" style={{ width: "85%" }}></div>
                      </div>
                      <p className="text-sm text-muted-foreground">6 active tickets (85% capacity)</p>
                    </div>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                </div>
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
