"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Download, TrendingUp, FileText, Users, Target } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts"

const transitionProgress = [
  { month: "Jan", knowledgeTransfer: 20, teamReadiness: 15, processDocumentation: 25 },
  { month: "Feb", knowledgeTransfer: 35, teamReadiness: 30, processDocumentation: 45 },
  { month: "Mar", knowledgeTransfer: 50, teamReadiness: 45, processDocumentation: 60 },
  { month: "Apr", knowledgeTransfer: 65, teamReadiness: 60, processDocumentation: 75 },
  { month: "May", knowledgeTransfer: 75, teamReadiness: 70, processDocumentation: 85 },
  { month: "Jun", knowledgeTransfer: 85, teamReadiness: 80, processDocumentation: 90 },
]

const knowledgeAcquisition = [
  { tower: "Application", articles: 45, sops: 28, videos: 12 },
  { tower: "Business", articles: 38, sops: 35, videos: 8 },
  { tower: "Data", articles: 32, sops: 22, videos: 15 },
  { tower: "Security", articles: 28, sops: 18, videos: 6 },
  { tower: "Infrastructure", articles: 42, sops: 30, videos: 10 },
]

const teamSkillAssessment = [
  { skill: "ERP Systems", current: 75, target: 90 },
  { skill: "Database Management", current: 68, target: 85 },
  { skill: "Process Automation", current: 82, target: 95 },
  { skill: "Troubleshooting", current: 78, target: 90 },
  { skill: "Customer Service", current: 85, target: 90 },
]

const effectivenessMetrics = [
  { metric: "Knowledge Retention", value: 82, target: 90 },
  { metric: "Process Adherence", value: 78, target: 85 },
  { metric: "Quality Score", value: 85, target: 90 },
  { metric: "Time to Competency", value: 75, target: 80 },
]

export default function AnalyticsPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Transition Analytics</h1>
            <p className="text-muted-foreground">Comprehensive analytics for transition management</p>
          </div>
          <div className="flex items-center gap-4">
            <Select defaultValue="last6months">
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select period" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="last3months">Last 3 months</SelectItem>
                <SelectItem value="last6months">Last 6 months</SelectItem>
                <SelectItem value="lastyear">Last year</SelectItem>
                <SelectItem value="custom">Custom range</SelectItem>
              </SelectContent>
            </Select>
            <Button className="flex items-center gap-1">
              <Download className="h-4 w-4" />
              Export Analytics
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Progress</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">78%</div>
              <p className="text-xs text-muted-foreground">+8% from last month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Knowledge Articles</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">185</div>
              <p className="text-xs text-muted-foreground">+15 this month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Team Readiness</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">80%</div>
              <p className="text-xs text-muted-foreground">+5% from last month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Effectiveness Score</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">82/100</div>
              <p className="text-xs text-muted-foreground">+3 from last quarter</p>
            </CardContent>
          </Card>
        </div>

        {/* Transition Progress Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Transition Progress Over Time</CardTitle>
            <CardDescription>Progress tracking across key transition areas</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={transitionProgress}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="knowledgeTransfer"
                  stackId="1"
                  stroke="#8884d8"
                  fill="#8884d8"
                  name="Knowledge Transfer"
                />
                <Area
                  type="monotone"
                  dataKey="teamReadiness"
                  stackId="1"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  name="Team Readiness"
                />
                <Area
                  type="monotone"
                  dataKey="processDocumentation"
                  stackId="1"
                  stroke="#ffc658"
                  fill="#ffc658"
                  name="Process Documentation"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Knowledge Acquisition by Tower */}
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Acquisition by Tower</CardTitle>
              <CardDescription>Documentation progress across different knowledge areas</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={knowledgeAcquisition}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="tower" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="articles" fill="#8884d8" name="Articles" />
                  <Bar dataKey="sops" fill="#82ca9d" name="SOPs" />
                  <Bar dataKey="videos" fill="#ffc658" name="Videos" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Team Skill Assessment */}
          <Card>
            <CardHeader>
              <CardTitle>Team Skill Assessment</CardTitle>
              <CardDescription>Current skill levels vs target competency</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {teamSkillAssessment.map((skill) => (
                  <div key={skill.skill} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{skill.skill}</span>
                      <span>
                        {skill.current}% / {skill.target}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full relative"
                        style={{ width: `${(skill.current / skill.target) * 100}%` }}
                      >
                        <div
                          className="absolute right-0 top-0 h-2 w-1 bg-gray-400 rounded-full"
                          style={{ right: `${100 - (skill.target / 100) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Effectiveness Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Transition Effectiveness Metrics</CardTitle>
            <CardDescription>Key performance indicators for transition success</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {effectivenessMetrics.map((metric) => (
                <div key={metric.metric} className="text-center">
                  <div className="text-2xl font-bold mb-2">{metric.value}%</div>
                  <div className="text-sm text-muted-foreground mb-2">{metric.metric}</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${(metric.value / metric.target) * 100}%` }}
                    />
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">Target: {metric.target}%</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
