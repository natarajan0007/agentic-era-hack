"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { mockTickets } from "@/lib/mock-data"
import { Clock, Search, Filter } from "lucide-react"
import Link from "next/link"
import { useAuthStore } from "@/lib/store"

export default function MyTicketsPage() {
  const { user } = useAuthStore()

  // Filter tickets based on user role
  const userTickets =
    user?.role === "end-user"
      ? mockTickets.filter((ticket) => ticket.reportedBy === "Priya Sharma") // For end users, show tickets they reported
      : mockTickets.filter((ticket) => ticket.assignedTo === user?.email) // For engineers, show assigned tickets

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
                <Input placeholder="Search tickets..." className="w-full" />
              </div>
              <Select defaultValue="all">
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="in-progress">In Progress</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                </SelectContent>
              </Select>
              <Select defaultValue="all">
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priorities</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Tickets List */}
        <Card>
          <CardHeader>
            <CardTitle>All Tickets</CardTitle>
            <CardDescription>
              Showing {userTickets.length} ticket{userTickets.length !== 1 ? "s" : ""}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {userTickets.length > 0 ? (
                userTickets.map((ticket) => (
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
                        {ticket.id} • {ticket.department} • Created: {new Date(ticket.createdAt).toLocaleDateString()}
                      </p>
                      <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>SLA: {new Date(ticket.slaDeadline).toLocaleString()}</span>
                      </div>
                    </div>
                    <Badge
                      variant={
                        ticket.status === "open"
                          ? "destructive"
                          : ticket.status === "in-progress"
                            ? "default"
                            : ticket.status === "resolved"
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
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
