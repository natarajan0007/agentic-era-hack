"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { mockTickets } from "@/lib/mock-data"
import { useParams } from "next/navigation"
import { Clock, User, Calendar, AlertTriangle, CheckCircle, ArrowUp } from "lucide-react"
import { AIAssistantPanel } from "@/components/ai-assistant-panel"
import { useState } from "react"
import toast from "react-hot-toast"

export default function TicketDetailsPage() {
  const params = useParams()
  const ticketId = params.id as string
  const ticket = mockTickets.find((t) => t.id === ticketId)
  const [resolution, setResolution] = useState("")

  if (!ticket) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold">Ticket not found</h1>
          <p className="text-muted-foreground">The ticket you're looking for doesn't exist.</p>
        </div>
      </AppLayout>
    )
  }

  const handleResolveTicket = () => {
    toast.success("Ticket resolved successfully!")
  }

  const handleEscalateTicket = () => {
    toast.success("Ticket escalated to L2 team")
  }

  const getSLAStatus = (deadline: string) => {
    const now = new Date()
    const slaDate = new Date(deadline)
    const hoursLeft = (slaDate.getTime() - now.getTime()) / (1000 * 60 * 60)

    if (hoursLeft < 0) return { status: "breached", color: "destructive", text: "SLA Breached" }
    if (hoursLeft < 2) return { status: "at-risk", color: "destructive", text: "At Risk" }
    return { status: "ok", color: "secondary", text: "On Track" }
  }

  const slaStatus = getSLAStatus(ticket.slaDeadline)

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Ticket Header */}
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold">{ticket.title}</h1>
              <Badge variant={ticket.priority === "high" ? "destructive" : "secondary"}>{ticket.priority}</Badge>
              <Badge variant={ticket.status === "open" ? "destructive" : "secondary"}>{ticket.status}</Badge>
            </div>
            <p className="text-muted-foreground">{ticket.id}</p>
          </div>

          <div className="flex space-x-2">
            <Button variant="outline" onClick={handleEscalateTicket}>
              <ArrowUp className="h-4 w-4 mr-2" />
              Escalate to L2
            </Button>
            <Button onClick={handleResolveTicket}>
              <CheckCircle className="h-4 w-4 mr-2" />
              Resolve Ticket
            </Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            {/* Ticket Information */}
            <Card>
              <CardHeader>
                <CardTitle>Ticket Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Reported by: {ticket.reportedBy}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Created: {new Date(ticket.createdAt).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">SLA Deadline: {new Date(ticket.slaDeadline).toLocaleString()}</span>
                    <Badge variant={slaStatus.color as any}>{slaStatus.text}</Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Department: {ticket.department}</span>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Description</h4>
                  <p className="text-sm text-muted-foreground">{ticket.description}</p>
                </div>

                {ticket.tags.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {ticket.tags.map((tag) => (
                        <Badge key={tag} variant="outline">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tabs for different information */}
            <Tabs defaultValue="similar" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="similar">Similar Tickets</TabsTrigger>
                <TabsTrigger value="sop">SOP Steps</TabsTrigger>
                <TabsTrigger value="resolutions">Top Resolutions</TabsTrigger>
                <TabsTrigger value="melt">MELT Data</TabsTrigger>
              </TabsList>

              <TabsContent value="similar" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Similar Tickets</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="p-3 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">INC-20250601-045</p>
                            <p className="text-sm text-muted-foreground">Invoice processing delays in ERP system</p>
                            <p className="text-xs text-muted-foreground">Resolved in 2 hours</p>
                          </div>
                          <Badge variant="outline">85% match</Badge>
                        </div>
                      </div>
                      <div className="p-3 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">INC-20250528-123</p>
                            <p className="text-sm text-muted-foreground">P2P system performance issues</p>
                            <p className="text-xs text-muted-foreground">Resolved in 4 hours</p>
                          </div>
                          <Badge variant="outline">78% match</Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="sop" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Relevant SOP Steps</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="p-3 border rounded-lg">
                        <h4 className="font-medium">Invoice Matching Error Resolution</h4>
                        <ol className="list-decimal list-inside text-sm text-muted-foreground mt-2 space-y-1">
                          <li>Log into SAP S/4HANA system</li>
                          <li>Navigate to Invoice Verification (MIRO)</li>
                          <li>Enter Invoice #INV-456789</li>
                          <li>Check tolerance settings in customization</li>
                          <li>Review price variance calculation</li>
                          <li>If variance is acceptable, adjust tolerance or approve manually</li>
                        </ol>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="resolutions" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>AI-Suggested Resolutions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium">Adjust Tolerance Settings</h4>
                          <Badge>Automated</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">
                          Increase price variance tolerance from ±2% to ±5% for this vendor category.
                        </p>
                        <Button size="sm">Execute Automated Fix</Button>
                      </div>

                      <div className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium">Manual Invoice Approval</h4>
                          <Badge variant="outline">Manual</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">
                          Review and manually approve the invoice if the price difference is justified.
                        </p>
                        <Button size="sm" variant="outline">
                          View Manual Steps
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="melt" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>MELT Data (Metrics, Events, Logs, Traces)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">System Metrics</h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>CPU Usage: 78%</div>
                          <div>Memory: 6.2GB/8GB</div>
                          <div>Response Time: 12.4s</div>
                          <div>Active Sessions: 245</div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Recent Events</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Database connection timeout</span>
                            <span className="text-muted-foreground">10:45 AM</span>
                          </div>
                          <div className="flex justify-between">
                            <span>High query execution time detected</span>
                            <span className="text-muted-foreground">10:42 AM</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>

            {/* Resolution Input */}
            <Card>
              <CardHeader>
                <CardTitle>Resolution Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  placeholder="Document your resolution steps and findings..."
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                  className="min-h-[100px]"
                />
                <Button className="mt-4">Save Resolution</Button>
              </CardContent>
            </Card>
          </div>

          {/* AI Assistant Panel */}
          <div>
            <AIAssistantPanel userRole="l1-engineer" ticketId={ticket.id} />
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
