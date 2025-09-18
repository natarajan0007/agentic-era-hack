"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { mockTickets } from "@/lib/mock-data"
import { Search, Filter, MoreHorizontal, UserPlus } from "lucide-react"
import Link from "next/link"
import { useState } from "react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import toast from "react-hot-toast"

export default function TicketManagementPage() {
  const [selectedStatus, setSelectedStatus] = useState("all")
  const [selectedPriority, setSelectedPriority] = useState("all")

  const filteredTickets = mockTickets.filter((ticket) => {
    if (selectedStatus !== "all" && ticket.status !== selectedStatus) return false
    if (selectedPriority !== "all" && ticket.priority !== selectedPriority) return false
    return true
  })

  const handleReassignTicket = (ticketId: string, newAssignee: string) => {
    toast.success(`Ticket ${ticketId} reassigned to ${newAssignee}`)
  }

  const getSLAStatus = (deadline: string) => {
    const now = new Date()
    const slaDate = new Date(deadline)
    const hoursLeft = (slaDate.getTime() - now.getTime()) / (1000 * 60 * 60)

    if (hoursLeft < 0) return { status: "breached", color: "destructive", text: "Breached" }
    if (hoursLeft < 2) return { status: "at-risk", color: "destructive", text: "At Risk" }
    return { status: "ok", color: "secondary", text: "On Track" }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Ticket Management</h1>
            <p className="text-muted-foreground">Manage and oversee all support tickets</p>
          </div>
          <Button>Create New Ticket</Button>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input placeholder="Search tickets..." className="pl-10" />
                </div>
              </div>
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="OPEN">Open</SelectItem>
                  <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                  <SelectItem value="RESOLVED">Resolved</SelectItem>
                  <SelectItem value="CLOSED">Closed</SelectItem>
                  <SelectItem value="ESCALATED">Escalated</SelectItem>
                </SelectContent>
              </Select>
              <Select value={selectedPriority} onValueChange={setSelectedPriority}>
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
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Tickets Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Tickets</CardTitle>
            <CardDescription>
              Showing {filteredTickets.length} of {mockTickets.length} tickets
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Ticket ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Assignee</TableHead>
                  <TableHead>SLA Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTickets.map((ticket) => {
                  const slaStatus = getSLAStatus(ticket.slaDeadline)
                  return (
                    <TableRow key={ticket.id}>
                      <TableCell className="font-medium">
                        <Link href={`/tickets/${ticket.id}`} className="hover:underline">
                          {ticket.id}
                        </Link>
                      </TableCell>
                      <TableCell className="max-w-[300px] truncate">{ticket.title}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            ticket.status === "OPEN"
                              ? "destructive"
                              : ticket.status === "IN_PROGRESS"
                                ? "default"
                                : "secondary"
                          }
                        >
                          {ticket.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={ticket.priority === "HIGH" ? "destructive" : "secondary"}>
                          {ticket.priority}
                        </Badge>
                      </TableCell>
                      <TableCell>{ticket.assignedTo?.split("@")[0] || "Unassigned"}</TableCell>
                      <TableCell>
                        <Badge variant={slaStatus.color as any}>{slaStatus.text}</Badge>
                      </TableCell>
                      <TableCell>{new Date(ticket.createdAt).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleReassignTicket(ticket.id, "L1 Engineer")}>
                              <UserPlus className="mr-2 h-4 w-4" />
                              Reassign to L1
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleReassignTicket(ticket.id, "L2 Engineer")}>
                              <UserPlus className="mr-2 h-4 w-4" />
                              Reassign to L2
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Link href={`/tickets/${ticket.id}`} className="flex items-center">
                                View Details
                              </Link>
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
