import { notFound } from "next/navigation";

import { api, ApiError } from "@/lib/api-client";
import type { MenuItem, Restaurant } from "@/types/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface RestaurantPageProps {
  params: Promise<{ id: string }>;
}

export default async function RestaurantPage({ params }: RestaurantPageProps) {
  const { id } = await params;

  let restaurant: Restaurant;
  let menu: MenuItem[];
  try {
    [restaurant, menu] = await Promise.all([
      api.get<Restaurant>(`/restaurants/${id}`),
      api.get<MenuItem[]>(`/restaurants/${id}/menu`),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  const byCategory = menu.reduce<Record<string, MenuItem[]>>((acc, item) => {
    (acc[item.category] ??= []).push(item);
    return acc;
  }, {});

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">{restaurant.name}</h1>
        <p className="text-muted-foreground">{restaurant.address}</p>
        <div className="mt-2 flex gap-2">
          <Badge>{restaurant.cuisine_type}</Badge>
          <Badge variant="secondary">{restaurant.rating.toFixed(1)} ★</Badge>
          <Badge variant="outline">{restaurant.price_range}</Badge>
        </div>
      </header>

      {Object.entries(byCategory).map(([category, items]) => (
        <section key={category} className="mb-6">
          <h2 className="mb-3 text-lg font-semibold">{category}</h2>
          <div className="grid gap-3">
            {items.map((item) => (
              <Card key={item.id}>
                <CardHeader className="flex-row items-start justify-between space-y-0">
                  <div>
                    <CardTitle className="text-base">{item.name}</CardTitle>
                    <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
                  </div>
                  <span className="whitespace-nowrap font-semibold">₹{item.price}</span>
                </CardHeader>
                <CardContent className="pt-0">
                  {item.is_vegetarian && <Badge variant="secondary">Veg</Badge>}
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      ))}
    </main>
  );
}
