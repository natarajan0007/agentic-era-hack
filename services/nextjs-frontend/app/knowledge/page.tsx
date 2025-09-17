"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Search, FileText, FileCode, Upload, ThumbsUp } from "lucide-react"
import Link from "next/link"

export default function KnowledgeBasePage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
            <p className="text-muted-foreground">Access documentation, SOPs, and technical resources</p>
          </div>
          <Button className="flex items-center gap-1">
            <Upload className="h-4 w-4" />
            Contribute
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search knowledge base..." className="pl-10" />
        </div>

        {/* Content Tabs */}
        <Tabs defaultValue="articles">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="articles">Articles</TabsTrigger>
            <TabsTrigger value="sops">SOPs</TabsTrigger>
            <TabsTrigger value="technical">Technical Docs</TabsTrigger>
            <TabsTrigger value="faq">FAQs</TabsTrigger>
          </TabsList>

          {/* Articles Tab */}
          <TabsContent value="articles" className="space-y-4 mt-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <Badge>ERP</Badge>
                    <div className="flex items-center text-muted-foreground text-sm">
                      <ThumbsUp className="h-3 w-3 mr-1" />
                      <span>24</span>
                    </div>
                  </div>
                  <CardTitle className="text-lg">Understanding Invoice Matching Process</CardTitle>
                  <CardDescription>Complete guide to 3-way matching in SAP</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Learn about the invoice matching process, common errors, and troubleshooting steps.
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">Updated 2 weeks ago</div>
                    <Link href="/knowledge/article-1">
                      <Button variant="outline" size="sm">
                        Read More
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <Badge>Performance</Badge>
                    <div className="flex items-center text-muted-foreground text-sm">
                      <ThumbsUp className="h-3 w-3 mr-1" />
                      <span>18</span>
                    </div>
                  </div>
                  <CardTitle className="text-lg">P2P System Performance Optimization</CardTitle>
                  <CardDescription>Best practices for system performance</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Guidelines for optimizing database queries, connection pools, and application settings.
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">Updated 1 month ago</div>
                    <Link href="/knowledge/article-2">
                      <Button variant="outline" size="sm">
                        Read More
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <Badge>Security</Badge>
                    <div className="flex items-center text-muted-foreground text-sm">
                      <ThumbsUp className="h-3 w-3 mr-1" />
                      <span>32</span>
                    </div>
                  </div>
                  <CardTitle className="text-lg">Access Management Guidelines</CardTitle>
                  <CardDescription>Security protocols for system access</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Procedures for granting, modifying, and revoking user access to procurement systems.
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">Updated 3 weeks ago</div>
                    <Link href="/knowledge/article-3">
                      <Button variant="outline" size="sm">
                        Read More
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-center mt-6">
              <Button variant="outline">Load More Articles</Button>
            </div>
          </TabsContent>

          {/* SOPs Tab */}
          <TabsContent value="sops" className="space-y-4 mt-6">
            <div className="grid gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="bg-muted p-2 rounded-lg">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium">Invoice Processing SOP</h3>
                        <Badge>Finance</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        Step-by-step procedure for processing invoices in the ERP system
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground">Last updated: June 1, 2025</div>
                        <Button variant="outline" size="sm">
                          View SOP
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="bg-muted p-2 rounded-lg">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium">Vendor Onboarding Process</h3>
                        <Badge>Procurement</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        Complete procedure for adding new vendors to the procurement system
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground">Last updated: May 15, 2025</div>
                        <Button variant="outline" size="sm">
                          View SOP
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="bg-muted p-2 rounded-lg">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium">System Backup and Recovery</h3>
                        <Badge>IT Operations</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        Procedures for regular backups and disaster recovery scenarios
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground">Last updated: April 28, 2025</div>
                        <Button variant="outline" size="sm">
                          View SOP
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Technical Docs Tab */}
          <TabsContent value="technical" className="space-y-4 mt-6">
            <div className="grid gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="bg-muted p-2 rounded-lg">
                      <FileCode className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium">Database Schema Documentation</h3>
                        <Badge>Technical</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        Complete documentation of the P2P system database schema and relationships
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground">Last updated: May 20, 2025</div>
                        <Button variant="outline" size="sm">
                          View Document
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="bg-muted p-2 rounded-lg">
                      <FileCode className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium">API Integration Guide</h3>
                        <Badge>Technical</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        Technical documentation for integrating with the procurement system APIs
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground">Last updated: June 5, 2025</div>
                        <Button variant="outline" size="sm">
                          View Document
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* FAQs Tab */}
          <TabsContent value="faq" className="space-y-4 mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Frequently Asked Questions</CardTitle>
                <CardDescription>Common questions and answers about the procurement system</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-b pb-4">
                  <h3 className="font-medium mb-2">How do I resolve invoice matching errors?</h3>
                  <p className="text-sm text-muted-foreground">
                    Invoice matching errors typically occur when there's a discrepancy between the purchase order, goods
                    receipt, and invoice. Check for price variances, quantity differences, or missing information. You
                    can adjust tolerance settings if the variance is acceptable or contact the vendor for corrections.
                  </p>
                </div>

                <div className="border-b pb-4">
                  <h3 className="font-medium mb-2">What causes performance slowdowns in the P2P system?</h3>
                  <p className="text-sm text-muted-foreground">
                    Common causes include database connection pool exhaustion, unoptimized queries, high concurrent user
                    load, or insufficient server resources. Check system logs for specific errors and monitor resource
                    utilization during peak hours.
                  </p>
                </div>

                <div className="border-b pb-4">
                  <h3 className="font-medium mb-2">How do I request new user access to the procurement system?</h3>
                  <p className="text-sm text-muted-foreground">
                    Submit a service request through the IT Service Portal with the user's details, required access
                    level, and business justification. Approvals are typically required from the department manager and
                    system owner before access is granted.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  )
}
