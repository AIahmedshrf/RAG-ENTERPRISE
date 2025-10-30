'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog'
import { modelsAPI, type AIModel, type ModelConfig, type Provider } from '@/app/lib/api/admin'
import { Plus, Trash2, Cpu, CheckCircle } from 'lucide-react'

export function ModelsManagement() {
  const [models, setModels] = useState<AIModel[]>([])
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [newModel, setNewModel] = useState<ModelConfig>({
    name: '',
    provider: 'azure',
    deployment_name: '',
    max_tokens: 2000,
    temperature: 0.7,
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [modelsData, providersData] = await Promise.all([
        modelsAPI.list(),
        modelsAPI.getProviders(),
      ])
      setModels(modelsData)
      setProviders(providersData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateModel = async () => {
    try {
      await modelsAPI.create(newModel)
      setDialogOpen(false)
      setNewModel({
        name: '',
        provider: 'azure',
        deployment_name: '',
        max_tokens: 2000,
        temperature: 0.7,
      })
      loadData()
    } catch (error) {
      console.error('Failed to create model:', error)
    }
  }

  const handleDeleteModel = async (modelId: string) => {
    if (!confirm('هل أنت متأكد من حذف هذا النموذج؟')) return

    try {
      await modelsAPI.delete(modelId)
      loadData()
    } catch (error) {
      console.error('Failed to delete model:', error)
    }
  }

  const getProviderBadge = (provider: string) => {
    const colors = {
      azure: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      openai: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      anthropic: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    }
    return colors[provider as keyof typeof colors] || colors.azure
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>إدارة النماذج</CardTitle>
          <Button onClick={() => setDialogOpen(true)} size="sm">
            <Plus className="w-4 h-4 ml-2" />
            نموذج جديد
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-muted-foreground">جاري التحميل...</p>
        ) : (
          <div className="space-y-3">
            {models.map((model) => (
              <div
                key={model.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <Cpu className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{model.name}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getProviderBadge(model.provider)}`}>
                        {model.provider}
                      </span>
                    </div>
                    {model.deployment_name && (
                      <p className="text-sm text-muted-foreground">
                        {model.deployment_name}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground">
                      تم الإنشاء: {new Date(model.created_at).toLocaleDateString('ar-SA')}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {model.status === 'active' && (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteModel(model.id)}
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      {/* Create Model Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>إضافة نموذج جديد</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">اسم النموذج</label>
              <Input
                value={newModel.name}
                onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
                placeholder="GPT-4"
              />
            </div>
            <div>
              <label className="text-sm font-medium">المزود</label>
              <select
                value={newModel.provider}
                onChange={(e) => setNewModel({ ...newModel, provider: e.target.value })}
                className="w-full h-10 px-3 rounded-md border border-input bg-background"
              >
                {providers.map((provider) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">اسم النشر (Deployment)</label>
              <Input
                value={newModel.deployment_name}
                onChange={(e) => setNewModel({ ...newModel, deployment_name: e.target.value })}
                placeholder="gpt-4"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Max Tokens</label>
                <Input
                  type="number"
                  value={newModel.max_tokens}
                  onChange={(e) => setNewModel({ ...newModel, max_tokens: parseInt(e.target.value) })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Temperature</label>
                <Input
                  type="number"
                  step="0.1"
                  value={newModel.temperature}
                  onChange={(e) => setNewModel({ ...newModel, temperature: parseFloat(e.target.value) })}
                />
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                إلغاء
              </Button>
              <Button onClick={handleCreateModel}>إضافة</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
