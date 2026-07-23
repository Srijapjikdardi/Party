import { notFound, useRouter } from 'next/navigation';
import { useState } from 'react';
import { api } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ToastProvider, toast } from '@/components/ui/use-toast';

export default function WaiterSessionBillPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const [sessionId] = params; // we'll await params later
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [splitType, setSplitType] = useState<'equal' | 'individual' | 'host_paid'>('equal');
  const [customAmounts, setCustomAmounts] = useState<Map<number, string>>(new Map());
  const [error, setError] = useState<string | null>(null);

  // Load session data
  (async () => {
    try {
      const res = await api.get(`/sessions/${await params.id}`);
      setSession(res);
      // Ensure user is host (we assume the route is protected; but we can double-check)
      // For simplicity, we just show error if not host later.
    } catch (err) {
      console.error('Failed to fetch session:', err);
      notFound();
    }
  })();

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const id = await params.id;
      // Prepare custom amounts object if needed
      const amountsObj: Record<string, number> = {};
      if (splitType === 'individual') {
        let total = 0;
        for (const [pid, amtStr] of customAmounts.entries()) {
          const amt = parseFloat(amtStr);
          if (isNaN(amt) || amt <= 0) {
            throw new Error(`Please enter valid amount for participant ${pid}`);
          }
          amountsObj[pid] = amt;
          total += amt;
        }
        // Optionally validate total matches session total? We'll let backend handle.
      }
      const res = await api.post(`/bills/session/${id}`, {
        split_type: splitType,
        custom_amounts: Object.keys(amountsObj).length ? amountsObj : undefined,
      });
      toast.success('Bill generated successfully!');
      // Redirect to bill view or session detail
      router.push(`/waiter/session/${id}`);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || err.message || 'Failed to generate bill');
    } finally {
      setLoading(false);
    }
  };

  if (!session) {
    return <div>Loading...</div>;
  }

  // Check if user is host (optional, but we can show warning)
  // We don't have current user info here; assume the route is protected by middleware or we rely on backend auth.

  return (
    <ToastProvider>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Generate Bill for Session {session.session_code}</h1>
        <p className="mb-4">Restaurant: {session.restaurant?.name}</p>
        <p className="mb-4">Status: {session.status}</p>

        <form onSubmit={handleGenerate} className="space-y-6">
          <div className="border rounded p-4">
            <div className="mb-4">
              <Label htmlFor="split-type">Split Type</Label>
              <Select
                id="split-type"
                value={splitType}
                onValueChange={(val) => {
                  setSplitType(val as any);
                  // Reset custom amounts when switching away from individual
                  if (val !== 'individual') {
                    setCustomAmounts(new Map());
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a split type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="equal">Equal Split</SelectItem>
                  <SelectItem value="individual">Individual Amounts</SelectItem>
                  <SelectItem value="host_paid">Host Pays All</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {splitType === 'individual' && session.participants && session.participants.length > 0 && (
              <div className="space-y-3">
                <Label htmlFor="custom-amounts">Enter amount for each participant (₹)</Label>
                <div className="space-y-2">
                  {session.participants.map((p: any) => (
                    <div key={participant.id} className="flex items-center space-x-3">
                      <Label htmlFor={`amt-${participant.id}" className="w-32"}>{participant.user.name}</Label>
                      <Input
                        id={`amt-${participant.id}`}
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="0.00"
                        value={customAmounts.get(participant.id) ?? ''}
                        onChange={(e) => {
                          const val = e.target.value;
                          if (val === '') {
                            const map = new Map(customAmounts);
                            map.delete(participant.id);
                            setCustomAmounts(map);
                          } else {
                            const map = new Map(customAmounts);
                            map.set(participant.id, val);
                            setCustomAmounts(map);
                          }
                        }}
                        className="w-24"
                      />
                    </div>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground">
                  Please ensure the sum of amounts matches the total session amount.
                </p>
              </div>
            )}

            {splitType === 'host_paid' && (
              <p className="text-sm text-muted-foreground">
                Host ({session.host_user?.name}) will pay the total amount. Others owe ₹0.
              </p>
            )}
          </div>

          <div className="flex justify-end">
            <Button type="submit" variant="default" disabled={loading} className="ml-2">
              {loading ? 'Generating...' : 'Generate Bill'}
            </Button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700">
            {error}
          </div>
        )}
      </div>
    </ToastProvider>
  );
}