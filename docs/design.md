# Product Design Direction: Agent-Ready Merchant

> **Purpose:** Define the visual and interaction direction for a professional, premium merchant control plane. This is design guidance only; it does not change platform authority, financial, or security contracts.

## 1. Product Character

The product should feel like a calm, high-trust **commerce command centre**: precise enough for financial operations, sophisticated enough for AI-native commerce, and simple enough for a merchant to act with confidence.

The current dark interface has a sound foundation, but it feels like a default developer dashboard because it relies on many equal-weight borders, compact text, repeated rectangular cards, and several competing accent colours. The direction is **cinematic restraint**: fewer but stronger surfaces, clearer hierarchy, and motion that explains the system rather than decorating it.

### Design principles

1. **Trust before spectacle.** Financial status, approvals, and irreversible actions are always clearer than effects.
2. **One visual voice.** Use the same spacing, elevation, radius, typography, and status language everywhere.
3. **Data leads the layout.** Emphasise the next merchant decision, live commerce health, and exceptional conditions.
4. **Motion has a job.** Animate state changes, loading, and the commerce pipeline; respect `prefers-reduced-motion`.
5. **Premium, never noisy.** Three.js/WebGL-inspired depth belongs mainly on the public landing page and demo storytelling—not behind operational data.

## 2. Visual Direction

### Core aesthetic

- **Base:** ink-black and midnight navy surfaces with a faint blue-violet atmospheric glow.
- **Structure:** soft translucent panels, hairline borders, restrained blur, and subtle radial gradients.
- **Accent:** a single electric indigo for navigation, focus, links, and primary actions.
- **State colours:** emerald, amber, and red are reserved for success, attention, and danger states.
- **Depth:** use shadow, surface contrast, and whitespace before adding more borders.
- **Typography:** a confident display face paired with a highly legible UI sans; mono only for IDs, hashes, and protocol traces.

### Colour palette

Use semantic tokens rather than hard-coded component colours. The following palette is the dark-mode baseline.

| Token | Hex | Usage |
| --- | --- | --- |
| `canvas` | `#070B14` | Application background |
| `surface-1` | `#0D1424` | Sidebar, primary cards |
| `surface-2` | `#141D31` | Raised cards, active panels |
| `surface-glass` | `rgba(20, 29, 49, 0.72)` | Glass surfaces over atmospheric backgrounds |
| `border-subtle` | `#24314A` | Default dividers and card boundaries |
| `border-strong` | `#344566` | Focused/selected panels |
| `text-primary` | `#F4F7FF` | Titles and primary data |
| `text-secondary` | `#A9B7D0` | Supporting content |
| `text-muted` | `#72819B` | Metadata and inactive UI |
| `brand` | `#7C5CFF` | Primary actions, selected navigation, focus |
| `brand-bright` | `#A78BFA` | Hover glow and hero gradient |
| `brand-deep` | `#4F46E5` | Pressed/strong brand treatment |
| `success` | `#34D399` | Paid, approved, verified, healthy |
| `warning` | `#FBBF24` | Pending approval, expiring, attention needed |
| `danger` | `#FB7185` | Rejection, destructive actions, failed settlement |
| `info` | `#38BDF8` | Informational system states and trace events |

**Accessibility:** retain 4.5:1 minimum text contrast; never distinguish operational state by colour alone; every status needs text and an icon/shape. Do not use gradients for critical values.

### Typography and spacing

- Display headings: `Space Grotesk` or `Manrope`; UI text: `Inter`; mono: `JetBrains Mono`.
- Use a 4 px spacing scale, 24–32 px between page sections, and 16–20 px within components.
- Page titles: 28–32 px; section titles: 18–20 px; body: 14 px; metadata: 12 px. Avoid essential text below 12 px.
- Prefer 12 px card radius and 10 px control radius. Keep full pills for compact status only.

## 3. Component System

### Application shell

- Give the sidebar a solid `surface-1` background and quiet brand mark; reduce permanent border weight.
- Group navigation into **Operate** (Overview, Approvals, Orders), **Manage** (Catalog, Inventory, Policies), and **Inspect** (Audit, Demo).
- Add a compact top-bar health indicator: system health, pending approval count, and merchant context.
- Make the active route a soft indigo surface with a 2 px left indicator rather than a fully saturated button.

### Cards, controls, and data

- Use cards only to group meaningful information. Avoid cards within cards unless the inset is actionable.
- Primary cards: `surface-1`, 1 px `border-subtle`, 12 px radius, and a small soft shadow.
- Interactive cards lift 2–4 px with a brighter border on hover; selected cards gain a brand-tinted glow and clear selection state.
- Use one filled primary button per view. Secondary actions are outline or ghost treatments.
- Inputs need clear labels, helpful constraints, inline validation, and larger hit targets. Monetary fields show the currency unit.
- Tables should be polished data grids: sticky headers, aligned values, responsive horizontal handling, row hover, and a detail drawer instead of overloaded rows.
- Timelines should show actor icon, state badge, concise event, timestamp, and expandable technical payload. Hashes and IDs stay secondary until expanded.

## 4. Page-Level Direction

### Public landing page

Create a high-impact hero with a dark atmospheric gradient and a restrained 3D/three.js-inspired visual: a floating commerce network showing **Buyer Agent → Policy Engine → Merchant Approval → Settlement → Audit**. It is illustrative only, lazy-loaded, and replaced by a static visual for reduced-motion or low-power devices.

Tell the product story below the hero:

1. Proof strip: floor price protected, payments verified, audit trail immutable.
2. Visual authoritative workflow.
3. Merchant dashboard preview with annotated control points.
4. Concise security and governance section.

### Dashboard

Answer three questions immediately: **What needs my attention? Is commerce healthy? What changed today?** Lead with the most urgent approval or settlement issue; follow with revenue, approvals, active orders, and inventory-risk KPIs, a live activity timeline, compact trend visuals, and a plain-language merchant autonomy card.

### Approvals

Turn the queue into a decision workbench. Surface requested price, floor price, margin impact, deadline, buyer context, and policy reason first. Keep approve, reject, and counter-offer in a fixed action area. Amber is only for genuinely pending or expiring decisions; historical tickets become quiet records.

### Catalog, orders, payments, and audit

- Catalogue cards use a consistent product render/placeholder, clear price hierarchy, stock health, and policy-guard status.
- Explain visually that floor price is an authority boundary, not a suggestion.
- Orders use a breathable data table with a status timeline in a detail drawer.
- Reconciliation explains why it is needed before it can be triggered.
- Audit resembles a trustworthy ledger: chronological events, chain-verification state, expandable evidence, and copyable IDs.

### Simulation sandbox

Make this the product showcase while retaining operational clarity. Scenarios should look like selectable missions with a small flow diagram and explicit outcome. During execution, animate only the active node; afterwards, present a timeline with policy verdict, financial impact, and audit confirmation as the three primary results.

## 5. Motion and Three.js Guidance

- Ordinary UI uses 150–220 ms ease-out CSS transitions, with no bouncing.
- Rich motion is limited to the landing hero and sandbox flow: ambient particles, connector lines, depth/parallax, and state pulses.
- Never run WebGL behind tables, forms, modals, or sensitive finance/approval interactions.
- Provide a static fallback and honour `prefers-reduced-motion`; motion must never block navigation or obscure text.
- Lazy-load 3D scenes and protect fast first load.

## 6. Visual References and Image Direction

These resources are inspiration for polish, motion, component craft, and design-system discipline—not templates to copy.

- [Beautiful UI](https://www.beautifului.dev/) — polished page composition and premium application surfaces.
- [BEUI](https://beui.dev/) and [Rare UI](https://www.rareui.com/) — distinctive component treatments and marketing-page rhythm.
- [Transitions](https://transitions.dev/) — restrained, meaningful motion patterns.
- [shadcn/ui](https://ui.shadcn.com/) and [ReUI](https://reui.io/components) — accessible primitives and interactions.
- [COSS UI](https://coss.com/ui) — expressive data/product storytelling.
- [UI Skills](https://www.ui-skills.com/) and [Design System Checklist](https://www.designsystemchecklist.com/) — consistency checks.

### Image references to source or create

Use abstract technology imagery rather than stock photos of people or generic e-commerce boxes.

1. **Hero visual:** deep indigo field with glass nodes, thin connection lines, and a protected commerce core. Build with Three.js, Spline/Rive, or a static SVG/PNG fallback.
2. **Product imagery:** consistent product cut-outs or gradient-backed renders; never mix unrelated stock-photo styles.
3. **Empty states:** small monochrome line illustrations with one brand glow (approval tray, verified shield, package node).
4. **Demo flow:** animated system diagram whose nodes map directly to genuine server-authoritative flow steps.

Moodboard image-search prompts: `dark indigo 3D glass network`, `futuristic commerce dashboard dark`, `abstract agent workflow visualization`, and `minimal dark data control room`. Verify external image licences before shipping an asset.

## 7. Implementation Order

1. Define semantic tokens for colour, type, radius, shadow, spacing, and motion.
2. Rebuild shared primitives: shell, navigation, controls, badges, cards, alerts, table, and detail drawer.
3. Redesign dashboard and approval queue first; they establish the product language.
4. Apply the system to catalog, orders, payments, policies, audit, and onboarding.
5. Build the landing hero and simulation flow with progressive enhancement and static fallbacks.
6. Verify responsive behaviour, keyboard navigation, contrast, reduced motion, and loading/error/empty states.

## 8. Non-Negotiable UX Safeguards

- Never imply that browser state or AI output is authoritative.
- Amounts remain unambiguous, consistently formatted as INR, and sourced from integer paise values.
- Policy decisions, approval state, payment settlement, idempotency, and audit evidence remain clear and cannot be hidden by visual flourish.
- Financial or destructive operations remain explicit, reviewable, and confirmation-driven when appropriate.

