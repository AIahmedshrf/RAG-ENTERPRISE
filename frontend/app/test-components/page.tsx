import { Button } from '@/app/components/ui/button'
import { Input } from '@/app/components/ui/input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/app/components/ui/card'

export default function TestComponents() {
  return (
    <div className="container mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold">اختبار المكونات</h1>
      
      {/* Buttons */}
      <Card>
        <CardHeader>
          <CardTitle>الأزرار</CardTitle>
          <CardDescription>أنواع مختلفة من الأزرار</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4 flex-wrap">
          <Button>افتراضي</Button>
          <Button variant="secondary">ثانوي</Button>
          <Button variant="outline">محدد</Button>
          <Button variant="destructive">خطر</Button>
          <Button variant="ghost">شفاف</Button>
          <Button size="sm">صغير</Button>
          <Button size="lg">كبير</Button>
        </CardContent>
      </Card>

      {/* Inputs */}
      <Card>
        <CardHeader>
          <CardTitle>حقول الإدخال</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="أدخل النص هنا..." />
          <Input type="email" placeholder="البريد الإلكتروني" />
          <Input type="password" placeholder="كلمة المرور" />
        </CardContent>
      </Card>

      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>بطاقة 1</CardTitle>
            <CardDescription>وصف البطاقة الأولى</CardDescription>
          </CardHeader>
          <CardContent>
            محتوى البطاقة هنا
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>بطاقة 2</CardTitle>
            <CardDescription>وصف البطاقة الثانية</CardDescription>
          </CardHeader>
          <CardContent>
            محتوى البطاقة هنا
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>بطاقة 3</CardTitle>
            <CardDescription>وصف البطاقة الثالثة</CardDescription>
          </CardHeader>
          <CardContent>
            محتوى البطاقة هنا
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
