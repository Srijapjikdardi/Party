import Link from "next/link";

import { api } from "@/lib/api-client";
import type { Restaurant } from "@/types/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

// Server component: fetched on the server, no client-side loading state
// needed for the initial render. See docs/MIGRATION_PLAN.md Phase 2 for
// which legacy screens map to server vs. client components.
export default async function HomePage() {
  const restaurants = await api.get<Restaurant[]>("/restaurants");

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">PartyPe</h1>
        <p className="text-muted-foreground">0% commission dining. Split the bill, not the friendship.</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {restaurants.map((restaurant) => (
          <Link key={restaurant.id} href={`/restaurants/${restaurant.id}`}>
            <Card className="h-full transition-shadow hover:shadow-md">
              <CardHeader>
                <div className="mb-1 flex items-center justify-between">
                  <CardTitle>{restaurant.name}</CardTitle>
                  <Badge variant="secondary">{Number(restaurant.rating).toFixed(1)} ★</Badge>
                </div>
                <CardDescription>{restaurant.cuisine_type} · {restaurant.price_range}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-2 text-sm text-muted-foreground">{restaurant.description}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  );
}
