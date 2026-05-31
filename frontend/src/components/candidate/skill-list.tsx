import { Badge } from "@/components/ui/badge";

export function SkillList({ skills, tone = "default" }: { skills: string[]; tone?: "default" | "success" | "danger" }) {
  const visible = skills.slice(0, 5);
  return (
    <div className="flex flex-wrap gap-1.5">
      {visible.map((skill) => <Badge key={skill} tone={tone}>{skill}</Badge>)}
      {skills.length > visible.length ? <Badge>+{skills.length - visible.length}</Badge> : null}
    </div>
  );
}

