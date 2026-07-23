import Link from 'next/link';
import { api } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '@/components/ui/card';

export default async function CustomerPage() {
  const sessions = await api.get('/sessions/me'); // endpoint for user's sessions
  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">My Sessions</h1>
      <div className="space-y-4">
        {sessions.map((s: any) => (
          <Card key={s.id} className="hover:shadow-md">
            <CardHeader>
              <CardTitle>{s.session_code}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Restaurant: {s.restaurant.name}</p>
              <p>Status:
                <Badge variant={s.status === 'active' ? 'secondary' : s.status === 'billing' ? 'outline' : s.status === 'closed' ? 'destructive' : 'secondary'}>
                  {s.status}
                </Badge>
              </p>
              <p>Total per person: ₹{s.share_amount ?? '0'}</p>
              <p>Paid: {s.is_paid ? 'Yes' : 'No'}</p>
              {s.status === 'billing' && !s.is_paid && (
                <Link href={`/customer/session/${s.id}/pay`} className="text-sm text-primary hover:underline mt-2 block">
                  Pay Now
                </Link>
              )}
              {!s.is_paid && s.status === 'closed' && (
                <Link href={`/customer/session/${s.id}/history`} className="text-sm text-primary hover:underline mt-2 block">
                  Receipt
                </Link>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}