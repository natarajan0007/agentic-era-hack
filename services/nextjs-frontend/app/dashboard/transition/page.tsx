"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { getDashboardMetrics } from "@/lib/api"
import { Calendar, FileText, TrendingUp, BarChart3, Upload } from "lucide-react"
import Link from "next/link"
import { ChatPanel } from "@/components/chat-panel"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAuthStore } from "@/lib/store"
import { useEffect, useState } from "react"

export default function TransitionDashboardPage() {
  const { user } = useAuthStore()
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      const fetchedMetrics = await getDashboardMetrics()
      setMetrics(fetchedMetrics)
      setLoading(false)
    }

    fetchData()
  }, [])

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Transition Dashboard</h1>
            <p className="text-muted-foreground">Monitor transition progress and knowledge acquisition</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Date Range:</span>
              <Select defaultValue="1year">
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select period" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3months">Last 3 months</SelectItem>
                  <SelectItem value="6months">Last 6 months</SelectItem>
                  <SelectItem value="1year">Last 1 year</SelectItem>
                  <SelectItem value="custom">Custom range</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        {loading || !metrics ? (
          <p>Loading metrics...</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Knowledge Articles</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.total_tickets}</div>
                <p className="text-xs text-muted-foreground">+12 from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">SOP Documents</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">89</div>
                <p className="text-xs text-muted-foreground">+8 from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Transition Progress</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">75%</div>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{ width: `75%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Effectiveness Score</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">82/100</div>
                <p className="text-xs text-muted-foreground">+5 from last quarter</p>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Transition Timeline */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Transition Timeline & Milestones</CardTitle>
                <CardDescription>Progress tracking of key transition activities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="relative pl-8 pb-8 border-l-2 border-primary">
                    <div className="absolute -left-2 top-0 h-4 w-4 rounded-full bg-primary"></div>
                    <div className="mb-1">
                      <span className="font-medium">Knowledge Transfer - Phase 1</span>
                      <Badge className="ml-2">Completed</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Core systems and processes documented</p>
                    <p className="text-xs text-muted-foreground flex items-center mt-1">
                      <Calendar className="h-3 w-3 mr-1" /> Completed on March 15, 2025
                    </p>
                  </div>

                  <div className="relative pl-8 pb-8 border-l-2 border-primary">
                    <div className="absolute -left-2 top-0 h-4 w-4 rounded-full bg-primary"></div>
                    <div className="mb-1">
                      <span className="font-medium">Shadow Support - Phase 1</span>
                      <Badge className="ml-2">Completed</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">L1 team shadowing completed</p>
                    <p className="text-xs text-muted-foreground flex items-center mt-1">
                      <Calendar className="h-3 w-3 mr-1" /> Completed on April 20, 2025
                    </p>
                  </div>

                  <div className="relative pl-8 pb-8 border-l-2 border-muted">
                    <div className="absolute -left-2 top-0 h-4 w-4 rounded-full bg-muted"></div>
                    <div className="mb-1">
                      <span className="font-medium">Knowledge Transfer - Phase 2</span>
                      <Badge variant="outline" className="ml-2">
                        In Progress
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Advanced troubleshooting and edge cases</p>
                    <p className="text-xs text-muted-foreground flex items-center mt-1">
                      <Calendar className="h-3 w-3 mr-1" /> Target: July 15, 2025
                    </p>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: "65%" }}></div>
                    </div>
                    <p className="text-xs text-right mt-1">65% complete</p>
                  </div>

                  <div className="relative pl-8">
                    <div className="absolute -left-2 top-0 h-4 w-4 rounded-full bg-muted"></div>
                    <div className="mb-1">
                      <span className="font-medium">Full Transition Completion</span>
                      <Badge variant="outline" className="ml-2">
                        Planned
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Complete handover of all support responsibilities</p>
                    <p className="text-xs text-muted-foreground flex items-center mt-1">
                      <Calendar className="h-3 w-3 mr-1" /> Target: September 30, 2025
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Knowledge Artifacts</CardTitle>
                  <CardDescription>Recently uploaded documentation and resources</CardDescription>
                </div>
                <Button className="flex items-center gap-1">
                  <Upload className="h-4 w-4" />
                  Upload New
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <p className="font-medium">P2P System Architecture Document</p>
                      <p className="text-sm text-muted-foreground">PDF • Uploaded 2 days ago</p>
                    </div>
                    <Badge>Application</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <p className="font-medium">Invoice Matching Process Flow</p>
                      <p className="text-sm text-muted-foreground">PPTX • Uploaded 5 days ago</p>
                    </div>
                    <Badge>Business</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <p className="font-medium">Database Schema Documentation</p>
                      <p className="text-sm text-muted-foreground">DOCX • Uploaded 1 week ago</p>
                    </div>
                    <Badge>Data</Badge>
                  </div>
                </div>
                <div className="mt-4 text-center">
                  <Link href="/transition-details" className="text-sm text-primary hover:underline">
                    View all artifacts
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AI Assistant Panel */}
          <div>
            <ChatPanel />
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
