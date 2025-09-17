export interface User {
  id: string
  name: string
  email: string
  role: "end-user" | "l1-engineer" | "l2-engineer" | "ops-manager" | "transition-manager"
  avatar?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

export const mockUsers: Record<string, User & { password: string }> = {
  "enduser@intellica.com": {
    id: "1",
    name: "John Doe",
    email: "enduser@intellica.com",
    role: "end-user",
    password: "password123",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  "l1@intellica.com": {
    id: "2",
    name: "Sarah Wilson",
    email: "l1@intellica.com",
    role: "l1-engineer",
    password: "password123",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  "l2@intellica.com": {
    id: "3",
    name: "Mike Johnson",
    email: "l2@intellica.com",
    role: "l2-engineer",
    password: "password123",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  "ops@intellica.com": {
    id: "4",
    name: "Lisa Chen",
    email: "ops@intellica.com",
    role: "ops-manager",
    password: "password123",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  "transition@intellica.com": {
    id: "5",
    name: "David Kumar",
    email: "transition@intellica.com",
    role: "transition-manager",
    password: "password123",
    avatar: "/placeholder.svg?height=40&width=40",
  },
}

export function authenticateUser(email: string, password: string): { user: User; token: string } | null {
  const user = mockUsers[email]
  if (user && user.password === password) {
    const { password: _, ...userWithoutPassword } = user
    return {
      user: userWithoutPassword,
      token: `mock-jwt-token-${user.id}`,
    }
  }
  return null
}
