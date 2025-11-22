import { useState } from 'react'
import { useAppStore } from '@/store/app'
import { uploadBook } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function FileUpload() {
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const addTask = useAppStore((state) => state.addTask)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
        }
    }

    const handleUpload = async () => {
        if (!file) return

        setUploading(true)
        try {
            const result = await uploadBook(file)

            addTask({
                id: result.file_id,
                filename: file.name,
                status: 'processing',
                progress: 0,
                message: 'Processing started...',
            })

            setFile(null)
            // Reset input
            const input = document.getElementById('file-input') as HTMLInputElement
            if (input) input.value = ''
        } catch (error) {
            console.error('Upload failed:', error)
            alert('Upload failed. Please try again.')
        } finally {
            setUploading(false)
        }
    }

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Upload Book</CardTitle>
                <CardDescription>
                    Upload your book file (TXT, MD, EPUB, PDF, DOCX) to convert to audiobook
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="flex flex-col gap-4">
                    <Input
                        id="file-input"
                        type="file"
                        accept=".txt,.md,.epub,.pdf,.docx"
                        onChange={handleFileChange}
                        disabled={uploading}
                    />
                    <Button onClick={handleUpload} disabled={!file || uploading}>
                        {uploading ? 'Uploading...' : 'Upload & Process'}
                    </Button>
                </div>
            </CardContent>
        </Card>
    )
}
