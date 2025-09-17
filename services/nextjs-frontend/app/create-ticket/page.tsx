"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { AppLayout } from "@/components/layout/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { useAuthStore } from "@/lib/store"
import { mockTickets } from "@/lib/mock-data"
import toast from "react-hot-toast"

const ticketSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  priority: z.enum(["low", "medium", "high", "critical"]),
  category: z.enum(["incident", "service", "problem", "change"]),
  department: z.string().min(1, "Department is required"),
})

type TicketForm = z.infer<typeof ticketSchema>

export default function CreateTicketPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<TicketForm>({
    resolver: zodResolver(ticketSchema),
    defaultValues: {
      priority: "medium",
      category: "incident",
      department: user?.role === "end-user" ? "Finance - Accounts Payable" : "",
    },
  })

  const onSubmit = (data: TicketForm) => {
    setIsSubmitting(true)

    try {
      // Create a new ticket object
      const newTicket = {
        id: `INC-${new Date().toISOString().slice(0, 10).replace(/-/g, "")}-${Math.floor(Math.random() * 10000).toString().padStart(5, "0")}`,
        title: data.title,
        description: data.description,
        status: "open",
        priority: data.priority,
        category: data.category,
        reportedBy: user?.name || "Unknown User",
        assignedTo: user?.role === "end-user" ? "l1@intellica.com" : undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        slaDeadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24 hours from now
        department: data.department,
        tags: [],
      }

      // Get existing tickets from localStorage or use empty array if none exist
      const existingTickets = JSON.parse(localStorage.getItem("tickets") || "[]") 

      // Add new ticket to the array
      const updatedTickets = [newTicket, ...existingTickets]

      // Save back to localStorage
      localStorage.setItem("tickets", JSON.stringify(updatedTickets))

      toast.success("Ticket created successfully!")
      reset()
      
      // Redirect to my-tickets page
      router.push("/my-tickets")
    } catch (error) {
      toast.error("Failed to create ticket")
      console.error(error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Create New Ticket</CardTitle>
            <CardDescription>
              {user?.role === "end-user" 
                ? "Report an issue or request a service" 
                : "Create a new ticket in the system"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  placeholder="Brief summary of the issue"
                  {...register("title")}
                  className={errors.title ? "border-red-500" : ""}
                />
                {errors.title && <p className="text-sm text-red-500">{errors.title.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Detailed description of the issue"
                  rows={5}
                  {...register("description")}
                  className={errors.description ? "border-red-500" : ""}
                />
                {errors.description && <p className="text-sm text-red-500">{errors.description.message}</p>}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select defaultValue="medium" {...register("priority")}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Select defaultValue="incident" {...register("category")}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="incident">Incident</SelectItem>
                      <SelectItem value="service">Service Request</SelectItem>
                      <SelectItem value="problem">Problem</SelectItem>
                      <SelectItem value="change">Change Request</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="department">Department</Label>
                <Input
                  id="department"
                  placeholder="Department name"
                  {...register("department")}
                  className={errors.department ? "border-red-500" : ""}
                />
                {errors.department && <p className="text-sm text-red-500">{errors.department.message}</p>}
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" type="button" onClick={() => router.back()}>Cancel</Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Creating..." : "Create Ticket"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}