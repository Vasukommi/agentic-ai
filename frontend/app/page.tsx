import Link from "next/link";
import {
  ArrowRight,
  Bot,
  Boxes,
  Cable,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const highlights = [
  {
    title: "App Router",
    description: "Server-first pages with a straightforward project structure.",
    icon: Boxes,
  },
  {
    title: "Typed UI",
    description: "Reusable primitives built on a shadcn-compatible foundation.",
    icon: Sparkles,
  },
  {
    title: "Backend-ready",
    description: "Clean enough to wire directly into your FastAPI service layer.",
    icon: Cable,
  },
];

const checklist = [
  "Next.js 16 with TypeScript",
  "Tailwind CSS v4 theme tokens",
  "Reusable Button, Badge, and Card primitives",
  "Responsive starter landing page",
];

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      <section className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-8 sm:px-8 lg:px-12">
        <div className="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[1.08fr_0.92fr]">
          <div className="space-y-8">
            <Badge variant="outline" className="w-fit bg-background/70 backdrop-blur">
              Next.js Frontend Ready
            </Badge>

            <div className="space-y-5">
              <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-balance sm:text-6xl">
                A clean frontend foundation for your AI product.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-muted-foreground sm:text-xl">
                Built with Next.js 16, Tailwind v4, and shadcn-compatible UI
                primitives so you can move straight into product work instead of
                spending time cleaning the starter.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button asChild size="lg">
                <a href="#stack">
                  Explore the stack
                  <ArrowRight className="size-4" />
                </a>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link href="https://nextjs.org/docs" target="_blank">
                  Next.js docs
                </Link>
              </Button>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {highlights.map(({ title, description, icon: Icon }) => (
                <Card
                  key={title}
                  className="border-border/70 bg-card/75 backdrop-blur-sm"
                >
                  <CardHeader className="space-y-3">
                    <div className="flex size-11 items-center justify-center rounded-2xl bg-secondary text-secondary-foreground">
                      <Icon className="size-5" />
                    </div>
                    <div className="space-y-1">
                      <CardTitle className="text-base">{title}</CardTitle>
                      <CardDescription>{description}</CardDescription>
                    </div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>

          <Card className="border-border/70 bg-card/82 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.35)] backdrop-blur-sm">
            <CardHeader className="space-y-4 border-b border-border/70">
              <Badge variant="secondary" className="w-fit">
                Starter Overview
              </Badge>
              <div className="space-y-2">
                <CardTitle className="text-2xl">
                  Simple structure, ready for backend integration.
                </CardTitle>
                <CardDescription className="text-sm sm:text-base">
                  The frontend is set up to stay small while giving you the
                  right primitives for a dashboard, product site, or internal
                  tool.
                </CardDescription>
              </div>
            </CardHeader>

            <CardContent className="space-y-6 pt-6">
              <div className="rounded-[calc(var(--radius)-0.25rem)] border border-border/70 bg-background/75 p-4">
                <div className="mb-3 flex items-center justify-between text-sm font-medium">
                  <span className="text-foreground">Run locally</span>
                  <span className="text-muted-foreground">frontend</span>
                </div>
                <code className="block rounded-2xl bg-slate-950 px-4 py-3 text-sm text-slate-100">
                  npm run dev
                </code>
              </div>

              <div id="stack" className="space-y-3">
                {checklist.map((item) => (
                  <div
                    key={item}
                    className="flex items-center gap-3 rounded-2xl border border-border/70 bg-background/60 px-4 py-3"
                  >
                    <CheckCircle2 className="size-4 text-primary" />
                    <span className="text-sm text-foreground/90">{item}</span>
                  </div>
                ))}
              </div>

              <div className="rounded-[calc(var(--radius)-0.25rem)] border border-dashed border-border/80 bg-muted/55 p-5">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 flex size-10 items-center justify-center rounded-2xl bg-accent text-accent-foreground">
                    <Bot className="size-5" />
                  </div>
                  <div className="space-y-2">
                    <p className="font-medium tracking-tight">
                      Recommended next step
                    </p>
                    <p className="text-sm leading-6 text-muted-foreground">
                      Add routes for auth, dashboard, and API integration once
                      your FastAPI endpoints are stable.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}
