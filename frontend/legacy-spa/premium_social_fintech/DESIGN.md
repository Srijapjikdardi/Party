---
name: Premium Social Fintech
colors:
  surface: '#faf9f7'
  surface-dim: '#dadad8'
  surface-bright: '#faf9f7'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f1'
  surface-container: '#efeeec'
  surface-container-high: '#e9e8e6'
  surface-container-highest: '#e3e2e0'
  on-surface: '#1a1c1b'
  on-surface-variant: '#474553'
  inverse-surface: '#2f3130'
  inverse-on-surface: '#f1f1ef'
  outline: '#787584'
  outline-variant: '#c8c4d5'
  surface-tint: '#584fbc'
  primary: '#3b309e'
  on-primary: '#ffffff'
  primary-container: '#534ab7'
  on-primary-container: '#d1ccff'
  inverse-primary: '#c5c0ff'
  secondary: '#5951b4'
  on-secondary: '#ffffff'
  secondary-container: '#9f97ff'
  on-secondary-container: '#33288d'
  tertiary: '#3e368b'
  on-tertiary: '#ffffff'
  tertiary-container: '#554ea4'
  on-tertiary-container: '#d1ccff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e3dfff'
  primary-fixed-dim: '#c5c0ff'
  on-primary-fixed: '#140067'
  on-primary-fixed-variant: '#3f35a3'
  secondary-fixed: '#e4dfff'
  secondary-fixed-dim: '#c5c0ff'
  on-secondary-fixed: '#140067'
  on-secondary-fixed-variant: '#41379b'
  tertiary-fixed: '#e4dfff'
  tertiary-fixed-dim: '#c5c0ff'
  on-tertiary-fixed: '#150264'
  on-tertiary-fixed-variant: '#423a8f'
  background: '#faf9f7'
  on-background: '#1a1c1b'
  surface-variant: '#e3e2e0'
  success-teal: '#1D9E75'
  celebration-coral: '#D85A30'
  wise-accent-green: '#9FE870'
  deep-forest: '#163300'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  title-md:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  unit-1: 8px
  unit-2: 16px
  unit-3: 24px
  unit-4: 32px
  unit-6: 48px
  margin-mobile: 20px
  margin-desktop: 40px
  gutter: 16px
---

## Brand & Style

This design system establishes a high-fidelity bridge between financial precision and the celebratory nature of social dining. The brand persona is that of a sophisticated host—organized and reliable, yet warm and energetic. It targets affluent, tech-savvy users who value seamless bill-splitting and group financial management.

The design style is **Corporate Modern with Tactile Warmth**. It draws inspiration from the utility of global fintech leaders like Wise, utilizing clean layouts and systematic clarity, but softens the experience with a warm "premium paper" background and vibrant accent pops. Visuals should prioritize high contrast and legible data visualization, while avoiding excessive skeuomorphism in favor of subtle, intentional depth.

## Colors

The palette is anchored by a deep **Primary Purple (#534AB7)**, chosen for its psychological associations with premium service and digital trust. This is supported by tonal variations that allow for sophisticated layering without introducing unnecessary hues.

- **Primary & Tones:** Used for core branding, active states, and primary actions.
- **Accents:** Teal is strictly reserved for financial success states (money received, paid in full), while Coral is used for price highlights, celebratory UI pops, and "urgent" dining notifications.
- **Backgrounds:** We deviate from sterile whites in favor of a warm, off-white paper tone (#F8F7F5) to create a more inviting, restaurant-like atmosphere. 
- **Contrast:** High contrast ratios must be maintained, specifically using the "Deep Forest" black-green for text to ensure legibility against the warm neutrals.

## Typography

The system utilizes a dual-sans approach. **Hanken Grotesk** is used for headlines to provide a sharp, contemporary "fintech" edge that feels more distinctive than standard system fonts. **Inter** handles all body and functional data for maximum legibility at small scales, particularly during complex bill calculations.

- **Hierarchy:** Use tight letter-spacing for large headlines to maintain a "high-fashion" editorial look.
- **Readability:** Maintain a 1.5x line-height ratio for body text to ensure ease of reading on mobile devices during active social events.
- **Numbers:** Tabular lining should be preferred for all financial figures to ensure currency symbols and decimals align perfectly in list views.

## Layout & Spacing

This design system follows a strict **8px Grid System**. All components, margins, and padding must be multiples of 8 to ensure visual harmony and developer efficiency.

- **Grid Strategy:** Use a **fluid grid** for mobile (4 columns) that transitions to a **fixed-max-width grid** for desktop (12 columns, 1140px max) to maintain the "app-like" intimacy even on larger screens.
- **Safe Zones:** Mobile layouts require a minimum 20px horizontal margin to prevent content from hitting device edges.
- **Vertical Rhythm:** Use generous vertical spacing (32px or 48px) between major sections to emphasize the "Minimalist" brand pillar and reduce cognitive load during payment flows.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** supplemented by a single, refined shadow style. Rather than multiple levels of shadows, the system uses "Surface" levels:

1.  **Level 0 (Base):** The #F8F7F5 background.
2.  **Level 1 (Cards):** Pure White (#FFFFFF) surfaces with a subtle `0 4px 12px rgba(0,0,0,0.1)` shadow.
3.  **Level 2 (Modals/Overlays):** Pure White (#FFFFFF) surfaces with a slightly deeper `0 8px 24px rgba(0,0,0,0.15)` shadow.

Avoid dark inner shadows or heavy glows. Borders should be used sparingly, primarily as subtle 1px dividers in a slightly darker neutral tone than the background to separate line items.

## Shapes

The shape language varies by component "weight" to create a friendly yet structured feel:

- **Primary Buttons:** 8px radius (Soft) to maintain a sense of precision and "clickability."
- **Cards & Modals:** 12px radius (Rounded) to soften the large surface areas and make the UI feel more approachable.
- **Badges, Pills, & Tags:** 20px+ radius (Pill-shaped) to distinguish them from interactive buttons and provide a playful, "social" contrast to the more rigid financial data.
- **Images/Avatars:** Avatars are always perfectly circular; food imagery within cards should follow the 12px card radius.

## Components

- **Buttons:** Primary buttons use the #534AB7 background with white text. High-emphasis social buttons (e.g., "Invite Friends") can utilize the #9FE870 accent to draw immediate attention.
- **Input Fields:** Use a minimal, "Wise-inspired" approach. A subtle 1px border that turns Primary Purple on focus. Labels should be small and positioned above the field.
- **Cards:** White backgrounds only. Use for restaurant info, split-bill summaries, and transaction history. Content should be padded by at least 16px (unit-2).
- **Chips & Badges:** Use the Pill-shaped radius. Use #1D9E75 (Teal) for "Paid" status and #D85A30 (Coral) for "Pending" or "Your Turn."
- **Lists:** Transaction lists should be high-contrast. Use Hanken Grotesk for the amount and Inter for the merchant/date.
- **Progress Indicators:** Use the Primary Purple for progress bars, indicating how much of a bill has been covered in real-time.