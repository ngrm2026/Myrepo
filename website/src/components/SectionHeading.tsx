export function SectionHeading({
  eyebrow,
  title,
  lead,
  center = false,
  light = false,
}: {
  eyebrow: string;
  title: string;
  lead?: string;
  center?: boolean;
  light?: boolean;
}) {
  return (
    <div className={center ? "mx-auto max-w-3xl text-center" : "max-w-3xl"}>
      <p className={`eyebrow ${light ? "text-brand-yellow" : ""}`}>
        <span className="h-0.5 w-6 bg-current" aria-hidden="true" />
        {eyebrow}
      </p>
      <h2 className={`section-title ${light ? "text-white" : ""}`}>{title}</h2>
      {lead && (
        <p className={`section-lead ${center ? "mx-auto" : ""} ${light ? "text-navy-100" : ""}`}>{lead}</p>
      )}
    </div>
  );
}
