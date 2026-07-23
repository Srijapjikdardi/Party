import Link from 'next/link';
import { api } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default async function RestaurantPage() {
  const restaurants = await api.get('/restaurants'); // In reality, filter by owner
  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Restaurant Dashboard</h1>
      <div className="space-y-4">
        {restaurants.map((r: any) => (
          <Card key={r.id} className="hover:shadow-md">
            <CardHeader>
              <CardTitle>{r.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{r.cuisine_type} · {r.price_range}</p>
              <p>{r.address}</p>
              <Link href={`/restaurant/${r.id}`} className="text-primary hover:underline">
                Manage
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}