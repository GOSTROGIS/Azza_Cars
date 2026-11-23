// Trip cost at published rates (market/trip_rates.json). The one implementation: the trip planner imports it,
// and tools/market/rental_charts.py runs it under node for the plan's trip-cost chart.
export function price(o, h, km, pvrtFrom) {
  const days = Math.floor(h / 24), rem = h - days * 24, whole = Math.ceil(h / 24);
  let base;
  if (o.model === "evo") base = days * o.per_day + (rem ? Math.min(rem * 60 * o.per_min, Math.ceil(rem) * o.per_hour, o.per_day) : 0);
  else if (o.model === "modo") {
    // Day Tripper covers whole-day bookings with a km allowance. Km beyond it are charged at the regular
    // per-km rate, which Modo does not state: an assumption.
    const tripper = o.day_tripper && h >= 24 ? whole * o.day_tripper + Math.max(0, km - whole * o.day_km) * o.per_km : Infinity;
    base = Math.min(h * o.per_hour + km * o.per_km, tripper);
  } else if (o.model === "tiers") base = days * o.tiers.at(-1)[1] + (rem ? (o.tiers.find(([hours]) => rem <= hours) || o.tiers.at(-1))[1] : 0);
  else if (o.model === "per_rental") base = whole * o.per_rental + km * o.per_km;
  else return NaN;
  return base + (o.trip_fee || 0) + (o.pvrt && h >= pvrtFrom ? o.pvrt * whole : 0);
}
