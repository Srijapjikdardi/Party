import { notFound } from 'next/navigation';
import { api, ApiError } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '@/components/ui/card';
import Link from 'next/link';

export default async function RestaurantDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let restaurant: any;
  try {
    restaurant = await api.get(`/restaurants/${id}`);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  const sessions = await api.get(`/restaurants/${id}/sessions`); // endpoint we might need to create later

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">{restaurant.name}</h1>
      <div className="mb-4">
        <p>{restaurant.cuisine_type} · {restaurant.price_range}</p>
        <p>{restaurant.address}</p>
      </div>

      <h2 className="font-bold mb-2">Active Sessions</h2>
      <div className="space-y-3">
        {sessions.map((s: any) => (
          <Card key={s.id} className="hover:shadow-sm">
            <CardHeader className="flex justify-between">
              <div>
                <CardTitle className="text">{s.session_code}</CardTitle>
                <p className="text-sm text-muted-foreground">Host: {s.host_user.name}</p>
              </div>
              <Badge variant={s.status === 'active' ? 'secondary' : s.status === 'billing' ? 'outline' : 'destructive'}>
                {s.status}
              </Badge>
            </CardHeader>
            <CardContent>
              <p>Participants: {s.participants.length}</p>
              <p>Orders: {s.orders.length}</p>
              <Link href={`/restaurant/${id}/session/${s.id}`} className="text-sm text-primary hover:underline">
                View Details
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}