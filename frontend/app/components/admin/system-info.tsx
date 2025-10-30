import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Server, CheckCircle } from 'lucide-react'

export function SystemInfo() {
  const systemData = [
    { label: 'الإصدار', value: '1.0.0' },
    { label: 'البيئة', value: process.env.NODE_ENV || 'development' },
    { label: 'Backend', value: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000' },
    { label: 'الحالة', value: 'تعمل', status: 'active' },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="w-5 h-5" />
          معلومات النظام
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {systemData.map((item) => (
            <div key={item.label} className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">{item.label}</span>
              <span className="text-sm font-medium flex items-center gap-2">
                {item.status === 'active' && (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                )}
                {item.value}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
