// Display labels. Body categories come from catalog/build_catalog.py BODY_MAP.
export const BODY_LABELS = {
  car: "Car",
  suv: "SUV",
  pickup: "Pickup",
  van: "Van / minivan",
  wagon: "Wagon",
  special: "Special purpose",
  mpv: "SUV or van (vPIC MPV)",
  truck: "Truck (vPIC)",
  bus: "Bus",
  lsv: "Low-speed vehicle",
};
export const BODY_ORDER = ["car", "suv", "pickup", "van", "wagon", "special", "mpv", "truck", "bus", "lsv"];

export const MARKETS = [
  { id: "US", label: "United States", basis: "listed by NHTSA vPIC or EPA fueleconomy.gov" },
  { id: "CA", label: "Canada", basis: "listed in NRCan Fuel Consumption Ratings" },
  { id: "MX", label: "Mexico", basis: "sales reported by INEGI RAIAVL" },
];

export const SOURCES = {
  vpic: { name: "NHTSA vPIC", what: "US federal vehicle make and model registry" },
  epa: { name: "EPA fueleconomy.gov", what: "US fuel economy data, size class" },
  nrcan: { name: "NRCan", what: "Canada fuel consumption ratings, vehicle class" },
  inegi: { name: "INEGI RAIAVL", what: "Mexico light-vehicle sales by model" },
  wikidata: { name: "Wikidata", what: "Open knowledge base, model items and dates" },
};

export const STATUS_LABELS = { current: "Current", discontinued: "Discontinued", unknown: "Status unknown" };

export const years = (m) => {
  const [a, b] = m.y;
  if (a == null && b == null) return "Years not stated";
  if (a === b || b == null) return String(a);
  if (a == null) return `until ${b}`;
  return `${a}–${b}`;
};
