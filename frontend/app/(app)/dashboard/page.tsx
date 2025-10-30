import { StatsOverview } from '@/app/components/admin/stats-overview'
import { Card, CardHeader, CardTitle, CardContent } from '@/app/components/ui/card'
import { Button } from '@/app/components/ui/button'
import Link from 'next/link'
import { MessageSquare, FileText, TrendingUp, ArrowRight } from 'lucide-react'

export default function DashboardPage() {
  const quickActions = [
    {
      title: 'بدء محادثة',
      description: 'اسأل أي سؤال عن مستنداتك',
      icon: MessageSquare,
      href: '/chat',
      color: 'bg-blue-500',
    },
    {
      title: 'رفع مستند',
      description: 'أضف مستندات جديدة للنظام',
      icon: FileText,
      href: '/documents',
      color: 'bg-green-500',
    },
    {
      title: 'تحليل مالي',
      description: 'احصل على رؤى مالية ذكية',
      icon: TrendingUp,
      href: '/financial',
      color: 'bg-purple-500',
    },
  ]

  return (
    <div className="h-full overflow-y-auto">
      <div className="border-b bg-background p-6">
        <h1 className="text-3xl font-bold">مرحباً بك في RAG-ENTERPRISE! 👋</h1>
        <p className="text-muted-foreground mt-2">
          نظام الذكاء الاصطناعي المتكامل لإدارة المستندات والتحليل المالي
        </p>
      </div>

      <div className="p-6 space-y-6">
        {/* Stats */}
        <StatsOverview />

        {/* Quick Actions */}
        <div>
          <h2 className="text-xl font-semibold mb-4">إجراءات سريعة</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <Link key={action.title} href={action.href}>
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                    <CardHeader>
                      <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center mb-3`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <CardTitle className="text-lg">{action.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground mb-4">
                        {action.description}
                      </p>
                      <Button variant="ghost" size="sm" className="group">
                        ابدأ الآن
                        <ArrowRight className="w-4 h-4 mr-2 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </CardContent>
                  </Card>
                </Link>
              )
            })}
          </div>
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>النشاط الأخير</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <p className="text-sm">لا توجد أنشطة حديثة</p>
              <p className="text-xs mt-1">ابدأ باستخدام النظام لرؤية الأنشطة هنا</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
