# Frontend

This folder contains the Next.js frontend for the project. It uses:

- Next.js 16 with the App Router
- TypeScript
- Tailwind CSS v4
- A small shadcn-compatible component base

## Getting Started

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Structure

- `app/`: routes, layout, and global styles
- `components/ui/`: reusable UI primitives
- `lib/`: shared utilities

## Extending the UI

The project includes `components.json`, aliases, and utility helpers so you can
continue adding shadcn-style components without reworking the setup.

## Build

```bash
npm run build
```
