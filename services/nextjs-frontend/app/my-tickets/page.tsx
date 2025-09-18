"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getTickets } from "@/lib/api"
import { Clock, Search, Filter } from "lucide-react"
import Link from "next/link"
import { useAuthStore } from "@/lib/store"
import { useEffect, useState, useMemo } from "react"

export default function MyTicketsPage() {
  const { user } = useAuthStore()
  const [tickets, setTickets] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState("all")
  const [priorityFilter, setPriorityFilter] = useState("all")
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    const fetchTickets = async () => {
      setLoading(true)
      const fetchedTickets = await getTickets()
      setTickets(fetchedTickets)
      setLoading(false)
    }

    fetchTickets()
  }, [])

  const filteredTickets = useMemo(() => {
    let filtered = Array.isArray(tickets) ? (
      user?.role === "end-user"
        ? tickets.filter((ticket) => ticket.reported_by_id === parseInt(user?.id))
        : tickets.filter((ticket) => ticket.assigned_to_id === parseInt(user?.id))
    ) : []

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
  }, [tickets, user, statusFilter, priorityFilter, searchTerm])

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">My Tickets</h1>
            <p className="text-muted-foreground">
              {user?.role === "end-user" ? "Tickets you've reported" : "Tickets assigned to you"}
            </p>
          </div>
          <Link href="/create-ticket">
            <Button>{user?.role === "end-user" ? "Report New Issue" : "Create Ticket"}</Button>
          </Link>
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
