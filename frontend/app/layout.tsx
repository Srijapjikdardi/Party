import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PartyPe",
  description: "0% commission dining platform — live bill splitting, merchant dashboard, waiter portal.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
