"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getTickets, getDashboardMetrics } from "@/lib/api"
import { Ticket } from "@/lib/mock-data"
import { Clock, CheckCircle, AlertCircle, TrendingUp, Ticket as TicketIcon, CircleDot, Loader, CheckCircle2, ArrowUpCircle, Search } from "lucide-react"
import Link from "next/link"
import { ChatPanel } from "@/components/chat-panel"
import { useAuthStore } from "@/lib/store"
import { useEffect, useState, useMemo } from "react"

export default function MyTicketsPage() {
  const { user } = useAuthStore()
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState("all")
  const [priorityFilter, setPriorityFilter] = useState("all")
  const [searchTerm, setSearchTerm] = useState("")
  const [view, setView] = useState(user?.role === 'end-user' ? 'reported' : 'assigned')

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

  const filteredTickets = useMemo(() => {
    let filtered = Array.isArray(tickets) ? tickets : []

    if (view === 'reported') {
      filtered = filtered.filter((ticket) => ticket.reporter?.id === parseInt(user?.id))
    } else {
      filtered = filtered.filter((ticket) => ticket.assignee?.id === parseInt(user?.id))
    }

    if (statusFilter !== "all") {
      filtered = filtered.filter((ticket) => ticket.status === statusFilter)
    }

    if (priorityFilter !== "all") {
      filtered = filtered.filter((ticket) => ticket.priority === priorityFilter)
    }

    if (searchTerm) {
      filtered = filtered.filter((ticket) =>
        ticket.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.id.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    return filtered
  }, [tickets, user, statusFilter, priorityFilter, searchTerm, view])

  const assignedTickets = tickets.filter(
    (ticket) => ticket.assignee?.email === user?.email && ["OPEN", "IN_PROGRESS"].includes(ticket.status),
  )

  const recentlyClosed = tickets.filter(
    (ticket) => ticket.assignee?.email === user?.email && ticket.status === "RESOLVED",
  )

  if (user?.role === 'end-user') {
    return (
      <AppLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">My Tickets</h1>
              <p className="text-muted-foreground">
                {view === 'reported' ? "Tickets you've reported" : "Tickets assigned to you"}
              </p>
            </div>
            <Link href="/create-ticket">
              <Button>{user?.role === "end-user" ? "Report New Issue" : "Create Ticket"}</Button>
            </Link>
          </div>

          {/* View Toggle */}
          <div className="flex space-x-2">
            <Button variant={view === 'reported' ? 'secondary' : 'outline'} onClick={() => setView('reported')}>
              Reported by me
            </Button>
            {user?.role !== 'end-user' && (
              <Button variant={view === 'assigned' ? 'secondary' : 'outline'} onClick={() => setView('assigned')}>
                Assigned to me
              </Button>
            )}
          </div>

          {/* Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <Input
                    placeholder="Search tickets..."
                    className="w-full"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="OPEN">Open</SelectItem>
                    <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                    <SelectItem value="RESOLVED">Resolved</SelectItem>
                    <SelectItem value="CLOSED">Closed</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Priorities</SelectItem>
                    <SelectItem value="LOW">Low</SelectItem>
                    <SelectItem value="MEDIUM">Medium</SelectItem>
                    <SelectItem value="HIGH">High</SelectItem>
                    <SelectItem value="CRITICAL">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Tickets List */}
          <Card>
            <CardHeader>
              <CardTitle>All Tickets</CardTitle>
              <CardDescription>
                Showing {filteredTickets.length} ticket{filteredTickets.length !== 1 ? "s" : ""}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-12">
                  <p>Loading tickets...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredTickets.length > 0 ? (
                    filteredTickets.map((ticket) => (
                      <div key={ticket.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <Link href={`/tickets/${ticket.id}`} className="font-medium hover:underline">
                              {ticket.title}
                            </Link>
                            <Badge variant={ticket.priority === "HIGH" || ticket.priority === "CRITICAL" ? "destructive" : "secondary"}>
                              {ticket.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {ticket.id} • {ticket.department?.name} • Created: {new Date(ticket.created_at).toLocaleDateString()}
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
                          <Badge
                            variant={
                              ticket.status === "OPEN"
                                ? "destructive"
                                : ticket.status === "IN_PROGRESS"
                                  ? "default"
                                  : ticket.status === "RESOLVED"
                                    ? "secondary"
                                    : "outline"
                            }
                          >
                            {ticket.status}
                          </Badge>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12">
                      <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-medium">No tickets found</h3>
                      <p className="text-muted-foreground">
                        {user?.role === "end-user"
                          ? "You haven't reported any tickets yet."
                          : "No tickets are currently assigned to you."}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    )
  }

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
