import { notFound } from 'next/navigation';
import { api } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '@/components/ui/card';

interface SessionData {
  id: string;
  session_code: string;
  status: string;
  restaurant: { name: string };
  participants: Array<{ id: number; user: { name: string }; share_amount: string; is_paid: boolean }>;
  orders: Array<{ id: string; customer_name: string; total_amount: string }>;
}

export default async function WaiterSessionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const session = await api.get<SessionData>(`/sessions/${id}`).catch(() => null);
  if (!session) notFound();

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Session {session.session_code}</h1>
      <div className="mb-4">
        <p>Restaurant: {session.restaurant.name}</p>
        <p>Status:
          <Badge variant={session.status === 'active' ? 'secondary' : session.status === 'billing' ? 'outline' : 'destructive'}>
            {session.status}
          </Badge>
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h2 className="font-bold mb-2">Participants</h2>
          <div className="space-y-2">
            {session.participants.map((p) => (
              <Card key={p.id} className="hover:shadow-sm">
                <CardHeader>
                  <CardTitle className="flex justify-between">
                    <span>{p.user.name}</span>
                    <Badge variant={p.is_paid ? 'secondary' : 'outline'}>
                      {p.is_paid ? 'Paid' : 'Pending'}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Amount: ₹{p.share_amount}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div>
          <h2 className="font-bold mb-2">Orders</h2>
          <div className="space-y-2">
            {session.orders.map((o) => (
              <Card key={o.id} className="hover:shadow-sm">
                <CardHeader>
                  <CardTitle>{o.customer_name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Total: ₹{o.total_amount}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {session.status === 'billing' && (
        <div className="mb-6 p-4 bg-gray-50 rounded">
          <h2 className="font-bold mb-2">Bill Ready</h2>
          <p>All orders placed. Ready to generate bill.</p>
        </div>
      )}
      {session.status === 'active' && (
        <div className="mt-6">
          <Link href={`/waiter/session/${id}/bill`} className="btn-primary px-4 py-2 rounded">
            Generate Bill
          </Link>
        </div>
      )}
    </main>
  );
}