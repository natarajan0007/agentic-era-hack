"use client"

import { useState, useEffect } from "react"
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
import { useAuthStore, useClonedTicketStore } from "@/lib/store"
import { getDepartments, createTicket } from "@/lib/api"
import toast from "react-hot-toast"

const ticketSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  priority: z.enum(["low", "medium", "high", "critical"]),
  category: z.enum(["incident", "service-request", "problem", "change", "hardware", "software", "network", "security"]),
  department_id: z.string().min(1, "Department is required"),
  tags: z.string().optional(),
  files: z.any().optional(),
})

type TicketForm = z.infer<typeof ticketSchema>

export default function CreateTicketPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const { clonedTicket, clearClonedTicket } = useClonedTicketStore()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [departments, setDepartments] = useState<any[]>([])

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    control,
    setValue,
  } = useForm<TicketForm>({
    resolver: zodResolver(ticketSchema),
    defaultValues: clonedTicket ? {
      title: `Copy of: ${clonedTicket.title}`,
      description: clonedTicket.description,
      priority: clonedTicket.priority,
      category: clonedTicket.category,
      department_id: clonedTicket.department_id.toString(),
      tags: clonedTicket.tags.map((tag: any) => tag.name).join(", "),
    } : {
      title: "",
      description: "",
      priority: "medium",
      category: "incident",
      department_id: "",
      tags: "",
    },
  })

  useEffect(() => {
    // Clear the cloned ticket from the store after the form is initialized
    if (clonedTicket) {
      clearClonedTicket()
    }
  }, [clonedTicket, clearClonedTicket])

  useEffect(() => {
    const fetchDepartments = async () => {
      const fetchedDepartments = await getDepartments()
      setDepartments(fetchedDepartments)
    }

    fetchDepartments()
  }, [])

  const onSubmit = async (data: TicketForm) => {
    setIsSubmitting(true)

    try {
      await createTicket(data)
      toast.success("Ticket created successfully!")
      reset()
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
                  <Select onValueChange={(value) => setValue("priority", value as any)} defaultValue={clonedTicket?.priority || "medium"}>
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
                  <Select onValueChange={(value) => setValue("category", value as any)} defaultValue={clonedTicket?.category || "incident"}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="incident">Incident</SelectItem>
                      <SelectItem value="service-request">Service Request</SelectItem>
                      <SelectItem value="problem">Problem</SelectItem>
                      <SelectItem value="change">Change Request</SelectItem>
                      <SelectItem value="hardware">Hardware</SelectItem>
                      <SelectItem value="software">Software</SelectItem>
                      <SelectItem value="network">Network</SelectItem>
                      <SelectItem value="security">Security</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="department_id">Department</Label>
                <Select onValueChange={(value) => setValue("department_id", value)} defaultValue={clonedTicket?.department_id?.toString() || ""}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map((dept) => (
                      <SelectItem key={dept.id} value={dept.id.toString()}>
                        {dept.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.department_id && <p className="text-sm text-red-500">{errors.department_id.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="tags">Tags</Label>
                <Input
                  id="tags"
                  placeholder="e.g., invoice, sap, error"
                  {...register("tags")}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="files">Attachments</Label>
                <Input
                  id="files"
                  type="file"
                  multiple
                  {...register("files")}
                />
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
