export interface Ticket {
  id: string
  title: string
  description: string
  status: "OPEN" | "IN_PROGRESS" | "RESOLVED" | "CLOSED" | "ESCALATED"
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  category: "INCIDENT" | "SERVICE" | "PROBLEM" | "CHANGE"
  reportedBy: string
  assignedTo?: string
  createdAt: string
  updatedAt: string
  slaDeadline: string
  department: string
  tags: string[]
  attachments?: string[]
  resolution?: string
  escalationReason?: string
}

export interface ChatMessage {
  id: string
  sender: "user" | "ai"
  message: string
  timestamp: string
  attachments?: string[]
}

export const mockTickets: Ticket[] = [
  {
    id: "INC-20250604-00123",
    title: "Invoice matching error - Price variance exceeds tolerance",
    description:
      'Invoice #INV-456789 from Vendor ABC Supplies Pvt. Ltd. is not matching with Purchase Order #PO-123456 in the ERP system (SAP S/4HANA). The system is throwing a "Price Variance Exceeds Tolerance" error during the 3-way match process.',
    status: "OPEN",
    priority: "HIGH",
    category: "INCIDENT",
    reportedBy: "Priya Sharma",
    assignedTo: "l1@intellica.com",
    createdAt: "2025-06-04T10:45:00Z",
    updatedAt: "2025-06-04T10:45:00Z",
    slaDeadline: "2025-06-04T18:45:00Z",
    department: "Finance - Accounts Payable",
    tags: ["ERP", "Invoice", "SAP", "Price Variance"],
    attachments: ["screenshot-error.png", "po-document.pdf", "grn-document.pdf"],
  },
  {
    id: "INC-20250604-NF-078",
    title: "Performance degradation in Procure-to-Pay solution",
    description:
      "Users are experiencing significant delays (10-15 seconds) when performing invoice matching in the custom-built Procure-to-Pay solution. The issue is intermittent but has increased in frequency since the last system patch.",
    status: "IN_PROGRESS",
    priority: "MEDIUM",
    category: "INCIDENT",
    reportedBy: "Priya Sharma",
    assignedTo: "l2@intellica.com",
    createdAt: "2025-06-04T11:15:00Z",
    updatedAt: "2025-06-04T14:30:00Z",
    slaDeadline: "2025-06-05T11:15:00Z",
    department: "Finance - Accounts Payable",
    tags: ["Performance", "P2P", "Custom Solution", "Database"],
  },
  {
    id: "SR-20250603-00045",
    title: "Request for new user access to procurement system",
    description: "New employee John Smith needs access to the procurement system with buyer role permissions.",
    status: "RESOLVED",
    priority: "LOW",
    category: "SERVICE",
    reportedBy: "HR Team",
    assignedTo: "l1@intellica.com",
    createdAt: "2025-06-03T09:00:00Z",
    updatedAt: "2025-06-03T16:30:00Z",
    slaDeadline: "2025-06-05T09:00:00Z",
    department: "Human Resources",
    tags: ["Access Request", "New User", "Procurement"],
    resolution: "User account created and access granted with buyer role permissions.",
  },
]

export const mockChatMessages: ChatMessage[] = [
  {
    id: "1",
    sender: "ai",
    message:
      "Hello! I'm your AI assistant. I'm here to help you report any IT issues you're experiencing. Could you please describe the problem you're facing?",
    timestamp: "2025-06-04T10:00:00Z",
  },
]

export const mockMetrics = {
  l1: {
    ticketsResolvedToday: 12,
    averageResolutionTime: "2.5 hours",
    csatScore: 4.2,
    slaCompliance: 95,
    activeTickets: 8,
    escalationRate: 15,
  },
  l2: {
    escalatedTicketsResolved: 5,
    rcaCompletionRate: 80,
    complexIssuesResolved: 3,
    averageResolutionTime: "4.2 hours",
    activeTickets: 6,
    knowledgeArticlesCreated: 2,
  },
  opsManager: {
    totalActiveTickets: 45,
    l1TeamPerformance: 92,
    l2TeamPerformance: 88,
    overallSlaCompliance: 94,
    criticalTickets: 3,
    breachedSlas: 2,
  },
  transition: {
    knowledgeArticles: 156,
    sopDocuments: 89,
    transitionProgress: 75,
    effectivenessScore: 82,
    artifactsUploaded: 234,
    teamReadiness: 78,
  },
}
