"use client"

import { useAuthStore } from "@/lib/store"
import { cn } from "@/lib/utils"
import { Brain, LayoutDashboard, Ticket, MessageSquare, Users, BarChart3, FileText, TrendingUp } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

const getNavigationItems = (role: string) => {
  switch (role) {
    case "end-user":
      return [
        { name: "AI Ticket Intake", href: "/ticket-intake", icon: Brain },
        { name: "Report Issue", href: "/create-ticket", icon: MessageSquare },
        { name: "My Tickets", href: "/my-tickets", icon: Ticket },
      ]
    case "l1-engineer":
      return [
        { name: "Dashboard", href: "/dashboard/l1", icon: LayoutDashboard },
        { name: "My Tickets", href: "/my-tickets", icon: Ticket },
        { name: "Knowledge Base", href: "/knowledge", icon: FileText },
      ]
    case "l2-engineer":
      return [
        { name: "Dashboard", href: "/dashboard/l2", icon: LayoutDashboard },
        { name: "My Tickets", href: "/my-tickets", icon: Ticket },
        { name: "Knowledge Base", href: "/knowledge", icon: FileText },
      ]
    case "ops-manager":
      return [
        { name: "Dashboard", href: "/dashboard/ops-manager", icon: LayoutDashboard },
        { name: "Ticket Management", href: "/ticket-management", icon: Ticket },
        { name: "Team Performance", href: "/team-performance", icon: Users },
        { name: "Reports", href: "/reports", icon: BarChart3 },
      ]
    case "transition-manager":
      return [
        { name: "Dashboard", href: "/dashboard/transition", icon: LayoutDashboard },
        { name: "Transition Details", href: "/transition-details", icon: TrendingUp },
        { name: "Knowledge Artifacts", href: "/knowledge-artifacts", icon: FileText },
        { name: "Analytics", href: "/analytics", icon: BarChart3 },
      ]
    default:
      return [{ name: "Dashboard", href: "/dashboard", icon: LayoutDashboard }]
  }
}

export function Sidebar() {
  const { user } = useAuthStore()
  const pathname = usePathname()

  if (!user) return null

  const navigationItems = getNavigationItems(user.role)

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="p-6">
        <div className="flex items-center space-x-2">
          <Brain className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold text-gray-900">Intellica</span>
        </div>
      </div>

      <nav className="mt-6">
        <div className="px-3">
          {navigationItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
                )}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
