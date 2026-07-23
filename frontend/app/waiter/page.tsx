import Link from 'next/link';
import { api } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default async function WaiterPage() {
  const sessions = await api.get('/sessions'); // assume endpoint exists
  return (
    <main className="p:6">
      <h1 className="text-2xl font-bold mb-4">Waiter Dashboard</h1>
      <div className="space-y-4">
        {sessions.map((s: any) => (
          <Card key={s.id} className="hover:shadow-md">
            <CardHeader>
              <CardTitle>{s.session_code}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Restaurant: {s.restaurant?.name}</p>
              <p>Status: {s.status}</p>
              <p>Participants: {s.participants?.length}</p>
              <Link href={`/waiter/session/${s.id}`} className="text-primary hover:underline">
                View Details
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}