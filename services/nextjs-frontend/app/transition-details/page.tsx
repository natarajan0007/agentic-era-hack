"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar, FileText, Users, CheckCircle, Clock, AlertCircle } from "lucide-react"

const milestones = [
  {
    id: 1,
    title: "Initial Assessment & Planning",
    status: "completed",
    progress: 100,
    startDate: "2025-01-15",
    endDate: "2025-02-15",
    description: "Complete assessment of current state and transition planning",
  },
  {
    id: 2,
    title: "Knowledge Transfer Phase 1",
    status: "completed",
    progress: 100,
    startDate: "2025-02-16",
    endDate: "2025-04-15",
    description: "Core system knowledge and basic processes",
  },
  {
    id: 3,
    title: "Shadow Support Phase",
    status: "in-progress",
    progress: 75,
    startDate: "2025-04-01",
    endDate: "2025-06-30",
    description: "Team members shadow existing support staff",
  },
  {
    id: 4,
    title: "Knowledge Transfer Phase 2",
    status: "in-progress",
    progress: 45,
    startDate: "2025-05-01",
    endDate: "2025-07-31",
    description: "Advanced troubleshooting and edge cases",
  },
  {
    id: 5,
    title: "Independent Operations",
    status: "planned",
    progress: 0,
    startDate: "2025-08-01",
    endDate: "2025-09-30",
    description: "Full transition to independent support operations",
  },
]

const knowledgeMetrics = [
  { category: "Application Knowledge", completed: 85, total: 120, percentage: 71 },
  { category: "Business Processes", completed: 92, total: 110, percentage: 84 },
  { category: "Technical Documentation", completed: 78, total: 95, percentage: 82 },
  { category: "Security Procedures", completed: 45, total: 60, percentage: 75 },
  { category: "Infrastructure", completed: 67, total: 80, percentage: 84 },
]

const riskAssessment = [
  {
    risk: "Knowledge Gap in Critical Systems",
    impact: "High",
    probability: "Medium",
    mitigation: "Additional training sessions scheduled",
    status: "active",
  },
  {
    risk: "Team Member Availability",
    impact: "Medium",
    probability: "Low",
    mitigation: "Cross-training multiple team members",
    status: "mitigated",
  },
  {
    risk: "Process Documentation Delays",
    impact: "Medium",
    probability: "Medium",
    mitigation: "Dedicated documentation resources assigned",
    status: "active",
  },
]

export default function TransitionDetailsPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Transition Details</h1>
          <p className="text-muted-foreground">Detailed view of transition progress and management</p>
        </div>

        {/* Overall Progress */}
        <Card>
          <CardHeader>
            <CardTitle>Overall Transition Progress</CardTitle>
            <CardDescription>Current status of the complete transition project</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-lg font-medium">75% Complete</span>
                <span className="text-sm text-muted-foreground">Target Completion: September 30, 2025</span>
              </div>
              <Progress value={75} className="h-3" />
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-green-600">3</div>
                  <div className="text-sm text-muted-foreground">Completed</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-600">2</div>
                  <div className="text-sm text-muted-foreground">In Progress</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-600">1</div>
                  <div className="text-sm text-muted-foreground">Planned</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="milestones">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="milestones">Milestones</TabsTrigger>
            <TabsTrigger value="knowledge">Knowledge Metrics</TabsTrigger>
            <TabsTrigger value="scorecard">Scorecard</TabsTrigger>
            <TabsTrigger value="risks">Risk Management</TabsTrigger>
          </TabsList>

          {/* Milestones Tab */}
          <TabsContent value="milestones" className="space-y-4 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Transition Milestones</CardTitle>
                <CardDescription>Key milestones and their current status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {milestones.map((milestone) => (
                    <div key={milestone.id} className="relative pl-8 pb-8 border-l-2 border-gray-200 last:border-l-0">
                      <div
                        className={`absolute -left-2 top-0 h-4 w-4 rounded-full ${
                          milestone.status === "completed"
                            ? "bg-green-500"
                            : milestone.status === "in-progress"
                              ? "bg-blue-500"
                              : "bg-gray-300"
                        }`}
                      />
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h3 className="font-medium">{milestone.title}</h3>
                          <Badge
                            variant={
                              milestone.status === "completed"
                                ? "default"
                                : milestone.status === "in-progress"
                                  ? "secondary"
                                  : "outline"
                            }
                          >
                            {milestone.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{milestone.description}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {milestone.startDate} - {milestone.endDate}
                          </span>
                        </div>
                        {milestone.status === "in-progress" && (
                          <div className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span>Progress</span>
                              <span>{milestone.progress}%</span>
                            </div>
                            <Progress value={milestone.progress} className="h-2" />
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Knowledge Metrics Tab */}
          <TabsContent value="knowledge" className="space-y-4 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Knowledge Acquisition Metrics</CardTitle>
                <CardDescription>Progress in knowledge transfer across different categories</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {knowledgeMetrics.map((metric) => (
                    <div key={metric.category} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{metric.category}</span>
                        <span className="text-sm text-muted-foreground">
                          {metric.completed}/{metric.total} items
                        </span>
                      </div>
                      <Progress value={metric.percentage} className="h-2" />
                      <div className="text-right text-sm text-muted-foreground">{metric.percentage}% complete</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Scorecard Tab */}
          <TabsContent value="scorecard" className="space-y-4 mt-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Knowledge Retention</CardTitle>
                  <CheckCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">85%</div>
                  <Progress value={85} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-1">Target: 90%</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Process Adherence</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">78%</div>
                  <Progress value={78} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-1">Target: 85%</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Team Readiness</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">82%</div>
                  <Progress value={82} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-1">Target: 90%</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Quality Score</CardTitle>
                  <CheckCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">88%</div>
                  <Progress value={88} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-1">Target: 90%</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Time to Competency</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">75%</div>
                  <Progress value={75} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-1">Target: 80%</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Overall Effectiveness</CardTitle>
                  <CheckCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">82/100</div>
                  <Progress value={82} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-1">Excellent progress</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Risk Management Tab */}
          <TabsContent value="risks" className="space-y-4 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Risk Assessment & Mitigation</CardTitle>
                <CardDescription>Identified risks and mitigation strategies</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {riskAssessment.map((risk, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-medium">{risk.risk}</h3>
                        <div className="flex items-center gap-2">
                          <Badge variant={risk.status === "active" ? "destructive" : "secondary"}>{risk.status}</Badge>
                          <AlertCircle
                            className={`h-4 w-4 ${risk.impact === "High" ? "text-red-500" : "text-yellow-500"}`}
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm mb-2">
                        <div>
                          <span className="text-muted-foreground">Impact: </span>
                          <Badge variant={risk.impact === "High" ? "destructive" : "secondary"}>{risk.impact}</Badge>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Probability: </span>
                          <Badge variant="outline">{risk.probability}</Badge>
                        </div>
                      </div>
                      <div className="text-sm">
                        <span className="text-muted-foreground">Mitigation: </span>
                        <span>{risk.mitigation}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  )
}
