import {
  Building2, CalendarCheck, Cable, Gauge, PanelsTopLeft, Power, Repeat, ToggleRight, Wrench, Zap,
} from "lucide-react";
import type { ServiceIconName } from "@/data/services";

const map = {
  repeat: Repeat,
  zap: Zap,
  power: Power,
  toggle: ToggleRight,
  panel: PanelsTopLeft,
  wrench: Wrench,
  cable: Cable,
  gauge: Gauge,
  calendar: CalendarCheck,
  building: Building2,
} satisfies Record<ServiceIconName, unknown>;

export function ServiceIcon({ name, className = "h-6 w-6" }: { name: ServiceIconName; className?: string }) {
  const Icon = map[name] ?? Zap;
  return <Icon className={className} aria-hidden="true" />;
}
