# Smart Audit Agent Design System

## Overview
This design system defines the UI foundations for the Smart Audit Agent frontend. It standardizes layout, typography, color, spacing, and component usage to ensure consistent, accessible, and scalable experiences.

## Design Principles
- **Clarity first**: content should be clear and readable at a glance.
- **Trust & credibility**: neutral backgrounds, calm accents, and high-contrast typography.
- **Consistency**: shared tokens and component patterns across all screens.
- **Accessibility**: WCAG AA contrast, visible focus states, keyboard-friendly flows.

## Foundations

### Typography
- **Primary font**: Inter (via Next.js font loader)
- **Scale**
  - Display: 36–44px
  - Headings: 24–32px
  - Body: 14–16px
  - Meta: 12–13px

### Color Tokens (Tailwind CSS Variables)
- **Primary**: Deep navy `--primary` (buttons, links)
- **Background**: Soft neutral `--background`
- **Foreground**: High-contrast `--foreground`
- **Secondary/Muted**: Soft slate for surfaces and helper text
- **Accent**: Light teal highlight for pills/badges
- **Destructive**: Standard red for errors
- **Border/Ring**: Subtle gray borders with primary ring on focus

### Spacing
- Base spacing follows an 8px rhythm.
- Use Tailwind spacing utilities (`p-6`, `gap-4`, `space-y-6`).

### Radius & Elevation
- Base radius: 12px (`--radius`)
- Cards: subtle shadow and border for light elevation.

## Components

### Button
- Variants: `default`, `secondary`, `outline`, `ghost`, `link`
- Sizes: `sm`, `default`, `lg`
- Usage: primary CTA for core actions, outline for secondary actions.

### Input & Label
- Labels always paired with inputs.
- Inputs use a clear active border (no extra focus ring) and disabled states.

### Card
- Primary layout primitive for forms and grouped content.

## Patterns

### Authentication Forms
- Title + description in hero header.
- Card container for form fields.
- Primary CTA + alternate action button.
- Invite-only access messaging with OTP recovery and verification flows.

## Accessibility Checklist
- Use semantic HTML elements for forms.
- Labels connected to inputs.
- Visible focus rings on interactive elements.
- Text contrast meets WCAG AA.

## Implementation Notes
- Tailwind config provides tokenized colors and radius values.
- Component utilities live under `components/ui`.
- Shared helper: `lib/utils.ts` with `cn()`.
