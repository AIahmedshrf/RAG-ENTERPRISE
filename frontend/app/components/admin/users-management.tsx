'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog'
import { usersAPI, type User, type UserCreate } from '@/app/lib/api/admin'
import { UserPlus, Trash2, Shield, User as UserIcon } from 'lucide-react'

export function UsersManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [newUser, setNewUser] = useState<UserCreate>({
    email: '',
    username: '',
    full_name: '',
    password: '',
    role: 'user',
  })

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const data = await usersAPI.list()
      setUsers(data)
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async () => {
    try {
      await usersAPI.create(newUser)
      setDialogOpen(false)
      setNewUser({
        email: '',
        username: '',
        full_name: '',
        password: '',
        role: 'user',
      })
      loadUsers()
    } catch (error) {
      console.error('Failed to create user:', error)
    }
  }

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('هل أنت متأكد من حذف هذا المستخدم؟')) return

    try {
      await usersAPI.delete(userId)
      loadUsers()
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  }

  const getRoleIcon = (role: string) => {
    return role === 'admin' ? <Shield className="w-4 h-4 text-amber-500" /> : <UserIcon className="w-4 h-4" />
  }

  const getRoleBadge = (role: string) => {
    const colors = {
      admin: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
      user: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      analyst: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    }
    return colors[role as keyof typeof colors] || colors.user
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>إدارة المستخدمين</CardTitle>
          <Button onClick={() => setDialogOpen(true)} size="sm">
            <UserPlus className="w-4 h-4 ml-2" />
            مستخدم جديد
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-muted-foreground">جاري التحميل...</p>
        ) : users.length === 0 ? (
          <div className="text-center py-8">
            <UserIcon className="w-12 h-12 mx-auto text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">لا يوجد مستخدمين</p>
            <Button onClick={() => setDialogOpen(true)} className="mt-4" size="sm">
              إنشاء أول مستخدم
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {users.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    {getRoleIcon(user.role)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{user.full_name}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getRoleBadge(user.role)}`}>
                        {user.role}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">@{user.username}</p>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-gray-400'}`} />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteUser(user.id)}
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      {/* Create User Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>إنشاء مستخدم جديد</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">الاسم الكامل</label>
              <Input
                value={newUser.full_name}
                onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                placeholder="أحمد محمد"
              />
            </div>
            <div>
              <label className="text-sm font-medium">اسم المستخدم</label>
              <Input
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                placeholder="ahmed"
              />
            </div>
            <div>
              <label className="text-sm font-medium">البريد الإلكتروني</label>
              <Input
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                placeholder="ahmed@example.com"
              />
            </div>
            <div>
              <label className="text-sm font-medium">كلمة المرور</label>
              <Input
                type="password"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                placeholder="••••••••"
              />
            </div>
            <div>
              <label className="text-sm font-medium">الدور</label>
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                className="w-full h-10 px-3 rounded-md border border-input bg-background"
              >
                <option value="user">مستخدم</option>
                <option value="admin">مدير</option>
                <option value="analyst">محلل</option>
              </select>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                إلغاء
              </Button>
              <Button onClick={handleCreateUser}>إنشاء</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
