import Link from 'next/link'
import { MessageSquare, FileText, DollarSign, Settings, LayoutDashboard } from 'lucide-react'
import { ThemeToggle } from '@/app/components/ui/theme-toggle'

const navigation = [
  { name: 'لوحة التحكم', href: '/dashboard', icon: LayoutDashboard },
  { name: 'المحادثة', href: '/chat', icon: MessageSquare },
  { name: 'المستندات', href: '/documents', icon: FileText },
  { name: 'التحليل المالي', href: '/financial', icon: DollarSign },
  { name: 'الإدارة', href: '/admin', icon: Settings },
]

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-l bg-card flex flex-col">
        <div className="p-6 border-b">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">RAG</span>
            </div>
            <div>
              <span className="font-semibold block">RAG-ENTERPRISE</span>
              <span className="text-xs text-muted-foreground">v1.0.0</span>
            </div>
          </Link>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                href={item.href}
                className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent transition-colors group"
              >
                <Icon className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">المظهر</span>
            <ThemeToggle />
          </div>
          <div className="text-xs text-muted-foreground">
            <p>© 2024 RAG-ENTERPRISE</p>
            <p className="mt-1">جميع الحقوق محفوظة</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  )
}
