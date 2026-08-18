# Edu Hub Design System

## Status

**Not yet designed or approved.**

Milestone 0 and Milestone 1 may create only the minimum neutral styling/components required to verify app shells, admin CRUD, responsive behavior, accessibility and engineering structure.

They must not lock a permanent visual system before the Creative Direction and Design + Systemize lifecycle phases.

## Current implementation rules

Until the production design system is approved:

- use semantic HTML
- keep component structure reusable where behavior genuinely repeats
- use accessible default form/control behavior
- support RTL structurally
- avoid hard-coding layout assumptions that make Arabic/long content difficult
- keep styling minimal and replaceable
- do not install a large UI framework solely to accelerate scaffolding
- do not treat a component library's default aesthetic as Edu Hub's identity
- prefer CSS/custom properties for a small neutral foundation when needed

## Responsive requirements

Even neutral foundation UI must be usable across:

- desktop
- intermediate/tablet widths
- mobile
- Arabic RTL
- long institution names/content
- keyboard/touch interaction

## Future production system

Phase 06 should define or approve:

- color tokens
- typography tokens and Arabic/Latin pairing
- spacing/fluid scales
- containers/grids
- radii/borders/elevation if used
- buttons/links
- form controls
- cards/list rows
- filters/search patterns
- navigation
- breadcrumbs
- profile data sections
- tables/comparison patterns
- trust/source/freshness indicators
- empty/loading/error states
- admin/control components
- responsive behavior
- motion states

## Authority

Once the project design system is approved, this document and the canonical production tokens/components take priority over framework defaults and reusable Admonk aesthetic preferences.
