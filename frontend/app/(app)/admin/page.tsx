import { StatsOverview } from '@/app/components/admin/stats-overview'
import { AgentsManager } from '@/app/components/admin/agents-manager'
import { SystemInfo } from '@/app/components/admin/system-info'
import { UsersManagement } from '@/app/components/admin/users-management'
import { ModelsManagement } from '@/app/components/admin/models-management'

export default function AdminPage() {
  return (
    <div className="h-full overflow-y-auto">
      <div className="border-b bg-background p-6">
        <h2 className="text-2xl font-semibold">⚙️ لوحة الإدارة</h2>
        <p className="text-sm text-muted-foreground mt-1">
          إدارة ومراقبة النظام الكاملة
        </p>
      </div>

      <div className="p-6 space-y-6">
        {/* Stats Overview */}
        <StatsOverview />

        {/* Users & Models Management */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <UsersManagement />
          <ModelsManagement />
        </div>

        {/* Agents & System Info */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AgentsManager />
          <SystemInfo />
        </div>
      </div>
    </div>
  )
}
