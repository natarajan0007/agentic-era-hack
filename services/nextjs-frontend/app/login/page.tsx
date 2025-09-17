"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { authenticateUser } from "@/lib/auth"
import { useAuthStore } from "@/lib/store"
import toast from "react-hot-toast"
import { Brain } from "lucide-react"

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const login = useAuthStore((state) => state.login)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)

    try {
      const result = authenticateUser(data.email, data.password)

      if (result) {
        login(result.user, result.token)
        toast.success("Login successful!")

        // Redirect based on user role
        switch (result.user.role) {
          case "end-user":
            router.push("/ticket-intake")
            break
          case "l1-engineer":
            router.push("/dashboard/l1")
            break
          case "l2-engineer":
            router.push("/dashboard/l2")
            break
          case "ops-manager":
            router.push("/dashboard/ops-manager")
            break
          case "transition-manager":
            router.push("/dashboard/transition")
            break
          default:
            router.push("/dashboard")
        }
      } else {
        toast.error("Invalid credentials")
      }
    } catch (error) {
      toast.error("Login failed")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <Brain className="h-12 w-12 text-primary" />
          </div>
          <CardTitle className="text-2xl font-bold">Intellica Platform</CardTitle>
          <CardDescription>AI-Powered IT Operations Management</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                {...register("email")}
                className={errors.email ? "border-red-500" : ""}
              />
              {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                {...register("password")}
                className={errors.password ? "border-red-500" : ""}
              />
              {errors.password && <p className="text-sm text-red-500">{errors.password.message}</p>}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <p className="text-sm font-medium mb-2">Demo Accounts:</p>
            <div className="text-xs space-y-1">
              <p>
                <strong>End User:</strong> enduser@intellica.com
              </p>
              <p>
                <strong>L1 Engineer:</strong> l1@intellica.com
              </p>
              <p>
                <strong>L2 Engineer:</strong> l2@intellica.com
              </p>
              <p>
                <strong>Ops Manager:</strong> ops@intellica.com
              </p>
              <p>
                <strong>Transition Manager:</strong> transition@intellica.com
              </p>
              <p className="mt-2">
                <strong>Password:</strong> password123
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
