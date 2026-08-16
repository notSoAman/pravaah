#PROJECT INDENTITY
This is the official website of PRAVAAH, a college mass-communication/media club.

#Tech stack
Django
Django Templates
Tailwind CSS
Alpine.js
PostgreSQL
GSAP (Only where genuinely useful)
HTMX (Only where genuinely useful)

#Design direction
Primary inspiration:
A24 Films

Visual characteristics:
- editorial
- cinematic
- minimal
- typography-heavy
- image-first
- large typography
- generous whitespace
- subtle animation
- monochrome UI
- fullscreen imagery

Avoid:
- SaaS aesthetic
- rounded dashboard cards
- excessive gradients
- excessive shadows
- generic Bootstrap styling
- excessive UI elements

#Architecture rules
- Django handles routing and data.
- Django Templates handle rendering.
- Reusable UI belongs in templates/components/.
- Do not introduce React.
- Do not introduce unnecessary dependencies.
- Use Tailwind for styling.
- Use Alpine.js only for small interactions.
- Keep JavaScript modular.
- Use semantic HTML.
- All content should be manageable through Django Admin.
