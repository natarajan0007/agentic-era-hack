"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { mockMetrics } from "@/lib/mock-data"
import { Users, CheckCircle, Award } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts"

const teamPerformanceData = [
  { name: "Sarah Wilson", role: "L1", ticketsResolved: 45, avgTime: "2.5h", satisfaction: 4.2, slaCompliance: 95 },
  { name: "Mike Johnson", role: "L2", ticketsResolved: 28, avgTime: "4.2h", satisfaction: 4.5, slaCompliance: 92 },
  { name: "Alex Chen", role: "L1", ticketsResolved: 38, avgTime: "3.1h", satisfaction: 4.0, slaCompliance: 88 },
  { name: "Emma Davis", role: "L2", ticketsResolved: 22, avgTime: "3.8h", satisfaction: 4.3, slaCompliance: 94 },
]

const weeklyTrends = [
  { week: "Week 1", l1Performance: 85, l2Performance: 88 },
  { week: "Week 2", l1Performance: 88, l2Performance: 85 },
  { week: "Week 3", l1Performance: 92, l2Performance: 90 },
  { week: "Week 4", l1Performance: 90, l2Performance: 92 },
]

export default function TeamPerformancePage() {
  const metrics = mockMetrics.opsManager

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Team Performance</h1>
          <p className="text-muted-foreground">Monitor and analyze team productivity and performance metrics</p>
        </div>

        {/* Overall Team Metrics */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">L1 Team Performance</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.l1TeamPerformance}%</div>
              <Progress value={metrics.l1TeamPerformance} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-1">+2% from last week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">L2 Team Performance</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.l2TeamPerformance}%</div>
              <Progress value={metrics.l2TeamPerformance} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-1">+5% from last week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall SLA Compliance</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.overallSlaCompliance}%</div>
              <Progress value={metrics.overallSlaCompliance} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-1">Target: 95%</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Team Members</CardTitle>
              <Award className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12</div>
              <p className="text-xs text-muted-foreground mt-1">8 L1 + 4 L2 Engineers</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Individual Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Individual Performance</CardTitle>
              <CardDescription>Performance metrics for each team member</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {teamPerformanceData.map((member) => (
                  <div key={member.name} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="font-medium">{member.name}</p>
                        <Badge variant="outline">{member.role}</Badge>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{member.ticketsResolved} tickets</p>
                        <p className="text-xs text-muted-foreground">this month</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Avg Time</p>
                        <p className="font-medium">{member.avgTime}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">CSAT</p>
                        <p className="font-medium">{member.satisfaction}/5</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">SLA</p>
                        <p className="font-medium">{member.slaCompliance}%</p>
                      </div>
                    </div>
                    <Progress value={member.slaCompliance} className="mt-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Performance Trends */}
          <Card>
            <CardHeader>
              <CardTitle>Weekly Performance Trends</CardTitle>
              <CardDescription>Team performance over the last 4 weeks</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weeklyTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="l1Performance" stroke="#8884d8" name="L1 Team" />
                  <Line type="monotone" dataKey="l2Performance" stroke="#82ca9d" name="L2 Team" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Team Workload Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Workload Distribution</CardTitle>
            <CardDescription>Current ticket distribution across team members</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={teamPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="ticketsResolved" fill="#8884d8" name="Tickets Resolved" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
