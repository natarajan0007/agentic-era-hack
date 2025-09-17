"use client"

import { AppLayout } from "@/components/layout/app-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Upload, Search, Filter, Download, FileText, Video, ImageIcon, File } from "lucide-react"
import { useState } from "react"
import toast from "react-hot-toast"

const artifacts = [
  {
    id: 1,
    name: "P2P System Architecture Document",
    type: "PDF",
    tower: "Application",
    uploadDate: "2025-06-01",
    uploader: "David Kumar",
    size: "2.4 MB",
    downloads: 45,
  },
  {
    id: 2,
    name: "Invoice Matching Process Flow",
    type: "PPTX",
    tower: "Business",
    uploadDate: "2025-05-28",
    uploader: "Sarah Wilson",
    size: "1.8 MB",
    downloads: 32,
  },
  {
    id: 3,
    name: "Database Schema Documentation",
    type: "DOCX",
    tower: "Data",
    uploadDate: "2025-05-25",
    uploader: "Mike Johnson",
    size: "3.2 MB",
    downloads: 28,
  },
  {
    id: 4,
    name: "Security Protocols Training Video",
    type: "MP4",
    tower: "Security",
    uploadDate: "2025-05-20",
    uploader: "Lisa Chen",
    size: "125 MB",
    downloads: 67,
  },
  {
    id: 5,
    name: "Infrastructure Setup Guide",
    type: "PDF",
    tower: "Infrastructure",
    uploadDate: "2025-05-15",
    uploader: "Alex Chen",
    size: "4.1 MB",
    downloads: 38,
  },
  {
    id: 6,
    name: "ERP System Screenshots",
    type: "ZIP",
    tower: "Application",
    uploadDate: "2025-05-10",
    uploader: "Emma Davis",
    size: "15.6 MB",
    downloads: 22,
  },
]

const towers = ["All Towers", "Application", "Business", "Data", "Security", "Infrastructure"]

export default function KnowledgeArtifactsPage() {
  const [selectedTower, setSelectedTower] = useState("All Towers")
  const [searchTerm, setSearchTerm] = useState("")

  const filteredArtifacts = artifacts.filter((artifact) => {
    if (selectedTower !== "All Towers" && artifact.tower !== selectedTower) return false
    if (searchTerm && !artifact.name.toLowerCase().includes(searchTerm.toLowerCase())) return false
    return true
  })

  const handleUpload = () => {
    toast.success("File uploaded successfully!")
  }

  const handleDownload = (artifactName: string) => {
    toast.success(`Downloading ${artifactName}`)
  }

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf":
      case "docx":
        return <FileText className="h-4 w-4" />
      case "mp4":
        return <Video className="h-4 w-4" />
      case "zip":
        return <File className="h-4 w-4" />
      case "pptx":
        return <ImageIcon className="h-4 w-4" />
      default:
        return <File className="h-4 w-4" />
    }
  }

  const getTowerColor = (tower: string) => {
    switch (tower) {
      case "Application":
        return "bg-blue-100 text-blue-800"
      case "Business":
        return "bg-green-100 text-green-800"
      case "Data":
        return "bg-purple-100 text-purple-800"
      case "Security":
        return "bg-red-100 text-red-800"
      case "Infrastructure":
        return "bg-orange-100 text-orange-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Knowledge Artifacts</h1>
            <p className="text-muted-foreground">Manage and access transition documentation and resources</p>
          </div>
          <Button onClick={handleUpload} className="flex items-center gap-1">
            <Upload className="h-4 w-4" />
            Upload New Artifact
          </Button>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {towers.slice(1).map((tower) => {
            const count = artifacts.filter((a) => a.tower === tower).length
            return (
              <Card key={tower}>
                <CardContent className="p-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{count}</div>
                    <div className="text-sm text-muted-foreground">{tower}</div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search artifacts..."
                    className="pl-10"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              <Select value={selectedTower} onValueChange={setSelectedTower}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by tower" />
                </SelectTrigger>
                <SelectContent>
                  {towers.map((tower) => (
                    <SelectItem key={tower} value={tower}>
                      {tower}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Artifacts Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Artifacts</CardTitle>
            <CardDescription>
              Showing {filteredArtifacts.length} of {artifacts.length} artifacts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Tower</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Uploader</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Downloads</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredArtifacts.map((artifact) => (
                  <TableRow key={artifact.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        {getFileIcon(artifact.type)}
                        <span className="max-w-[300px] truncate">{artifact.name}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{artifact.type}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getTowerColor(artifact.tower)}>{artifact.tower}</Badge>
                    </TableCell>
                    <TableCell>{new Date(artifact.uploadDate).toLocaleDateString()}</TableCell>
                    <TableCell>{artifact.uploader}</TableCell>
                    <TableCell>{artifact.size}</TableCell>
                    <TableCell>{artifact.downloads}</TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownload(artifact.name)}
                        className="flex items-center gap-1"
                      >
                        <Download className="h-3 w-3" />
                        Download
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
