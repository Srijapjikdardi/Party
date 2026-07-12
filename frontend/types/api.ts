// Mirrors backend/app/schemas/*.py — keep these in sync manually until
// the migration reaches the point of generating this file from the
// FastAPI OpenAPI schema (see docs/MIGRATION_PLAN.md, Phase 4).

export interface Restaurant {
  id: number;
  name: string;
  address: string;
  phone: string;
  cuisine_type: string;
  rating: number;
  price_range: string;
  description: string;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MenuItem {
  id: number;
  restaurant_id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  image_url: string | null;
  is_available: boolean;
  is_vegetarian: boolean;
  created_at: string;
  updated_at: string;
}

export interface RestaurantTable {
  id: number;
  restaurant_id: number;
  number: string;
  capacity: number;
  status: "available" | "occupied" | "reserved" | "billing";
}

export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: "diner" | "merchant" | "waiter" | "admin";
  avatar_url: string | null;
  wallet_balance: number;
  created_at: string;
}

export interface Order {
  id: number;
  user_id: number | null;
  session_id: number | null;
  customer_name: string;
  customer_phone: string;
  total_amount: number;
  status: "pending" | "confirmed" | "preparing" | "ready" | "delivered" | "cancelled";
  special_instructions: string | null;
  restaurant_id: number;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}
