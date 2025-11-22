import { useEffect, useState } from 'react'
import { useAppStore } from '@/store/app'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loader2, Plus, ArrowRight } from 'lucide-react'

export function ProjectList({ onSelect }: { onSelect: (id: string) => void }) {
    const { projects, fetchProjects, createProject, loading } = useAppStore()
    const [uploading, setUploading] = useState(false)

    useEffect(() => {
        fetchProjects()
    }, [])

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setUploading(true)
            await createProject(e.target.files[0])
            setUploading(false)
        }
    }

    return (
        <div className="container mx-auto p-8 max-w-5xl">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">My Projects</h1>
                    <p className="text-muted-foreground">Manage your audiobook productions</p>
                </div>
                <div className="flex items-center gap-2">
                    <Input
                        id="file-upload"
                        type="file"
                        className="hidden"
                        accept=".txt,.epub,.md"
                        onChange={handleUpload}
                        disabled={uploading}
                    />
                    <Button asChild disabled={uploading}>
                        <label htmlFor="file-upload" className="cursor-pointer">
                            {uploading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
                            New Project
                        </label>
                    </Button>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {projects.map((project) => (
                    <Card key={project.id} className="hover:bg-accent/50 transition-colors cursor-pointer" onClick={() => onSelect(project.id)}>
                        <CardHeader className="pb-2">
                            <div className="flex justify-between items-start">
                                <CardTitle className="text-lg truncate" title={project.name}>{project.name}</CardTitle>
                                <Badge variant={
                                    project.status === 'completed' ? 'default' :
                                        project.status === 'failed' ? 'destructive' : 'secondary'
                                }>
                                    {project.status}
                                </Badge>
                            </div>
                            <CardDescription>
                                Updated {new Date(project.updated_at).toLocaleDateString()}
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="flex justify-end">
                                <Button variant="ghost" size="sm" className="gap-1">
                                    Open Studio <ArrowRight className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {projects.length === 0 && !loading && (
                    <div className="col-span-full text-center py-12 text-muted-foreground border-2 border-dashed rounded-lg">
                        No projects yet. Create one to get started.
                    </div>
                )}
            </div>
        </div>
    )
}
