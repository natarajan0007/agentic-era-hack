"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { AppLayout } from "@/components/layout/app-layout"
import { getTicketById, escalateTicket } from "@/lib/api"
import { useClonedTicketStore } from "@/lib/store"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Clock, User, Tag, Paperclip } from "lucide-react"
import toast from "react-hot-toast"

export default function TicketDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string
  const [ticket, setTicket] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [escalationReason, setEscalationReason] = useState("")
  const setClonedTicket = useClonedTicketStore((state) => state.setClonedTicket)

  useEffect(() => {
    if (id) {
      const fetchTicket = async () => {
        setLoading(true)
        try {
          const fetchedTicket = await getTicketById(id)
          if (fetchedTicket) {
            setTicket(fetchedTicket)
          } else {
            setError("Ticket not found.")
          }
        } catch (err) {
          setError("Failed to fetch ticket.")
        } finally {
          setLoading(false)
        }
      }
      fetchTicket()
    }
  }, [id])

  const handleEscalate = async () => {
    if (!escalationReason) {
      toast.error("Please provide a reason for escalation.")
      return
    }
    try {
      await escalateTicket(id, escalationReason)
      toast.success("Ticket escalated successfully!")
      setTicket({ ...ticket, status: "ESCALATED" })
      setEscalationReason("")
    } catch (error) {
      toast.error("Failed to escalate ticket.")
    }
  }

  const handleClone = () => {
    setClonedTicket(ticket)
    router.push("/create-ticket")
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <p>Loading ticket details...</p>
        </div>
      </AppLayout>
    )
  }

  if (error) {
    return (
      <AppLayout>
        <div className="text-center py-12 text-red-500">
          <p>{error}</p>
        </div>
      </AppLayout>
    )
  }

  if (!ticket) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <p>Ticket not found.</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-3xl font-bold">{ticket.title}</CardTitle>
                <CardDescription className="mt-2">
                  Ticket ID: {ticket.id}
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
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
                  className="text-lg"
                >
                  {ticket.status}
                </Badge>
                <Button variant="outline" onClick={handleClone}>Clone</Button>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="outline">Escalate</Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Escalate Ticket</AlertDialogTitle>
                      <AlertDialogDescription>
                        Please provide a reason for escalating this ticket.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <Input
                      placeholder="Reason for escalation"
                      value={escalationReason}
                      onChange={(e) => setEscalationReason(e.target.value)}
                    />
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleEscalate}>Escalate</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">{ticket.description}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <h4 className="font-semibold">Priority</h4>
                <Badge variant={ticket.priority === "HIGH" || ticket.priority === "CRITICAL" ? "destructive" : "secondary"}>
                  {ticket.priority}
                </Badge>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Category</h4>
                <p className="text-muted-foreground">{ticket.category}</p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Department</h4>
                <p className="text-muted-foreground">{ticket.department?.name || 'N/A'}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="flex items-center space-x-2">
                    <User className="h-5 w-5 text-muted-foreground" />
                    <div>
                        <h4 className="font-semibold">Reported By</h4>
                        <p className="text-muted-foreground">{ticket.reporter?.name || 'N/A'}</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <User className="h-5 w-5 text-muted-foreground" />
                    <div>
                        <h4 className="font-semibold">Assigned To</h4>
                        <p className="text-muted-foreground">{ticket.assignee?.name || 'Not Assigned'}</p>
                    </div>
                </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex items-center space-x-2">
                    <Clock className="h-5 w-5 text-muted-foreground" />
                    <div>
                        <h4 className="font-semibold">Created At</h4>
                        <p className="text-muted-foreground">{new Date(ticket.created_at).toLocaleString()}</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <Clock className="h-5 w-5 text-muted-foreground" />
                    <div>
                        <h4 className="font-semibold">SLA Deadline</h4>
                        <p className="text-muted-foreground">{new Date(ticket.sla_deadline).toLocaleString()}</p>
                    </div>
                </div>
            </div>

            {ticket.tags && ticket.tags.length > 0 && (
              <div className="flex items-center space-x-2">
                <Tag className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h4 className="font-semibold">Tags</h4>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {ticket.tags.map((tag: any) => (
                      <Badge key={tag.id} variant="secondary">{tag.name}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {ticket.attachments && ticket.attachments.length > 0 && (
              <div className="flex items-center space-x-2">
                <Paperclip className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h4 className="font-semibold">Attachments</h4>
                  <ul className="list-disc list-inside mt-2">
                    {ticket.attachments.map((att: any) => (
                      <li key={att.id}>
                        <a href={att.file_path} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                          {att.file_name}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}