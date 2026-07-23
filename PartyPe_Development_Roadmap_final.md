# PartyPe Development Roadmap

## Vision

Production-ready collaborative restaurant ordering, dining session, bill
splitting, and restaurant management platform.

## Tech Stack

### Frontend

-   Next.js 15
-   React
-   TypeScript
-   Tailwind CSS
-   shadcn/ui

### Backend

-   FastAPI
-   SQLModel
-   Alembic
-   PostgreSQL (Neon)

### Authentication

-   bcrypt
-   JWT
-   Refresh Tokens

### Payments

-   Razorpay

### Realtime

-   FastAPI WebSockets

### Storage

-   Cloudinary

### Deployment

-   Vercel
-   Railway/Render
-   Neon

### Monitoring

-   Sentry

## Engineering Rules

-   One chat = one milestone.
-   Inspect repository first.
-   Fix regressions before new features.
-   No TODOs.
-   No placeholder code.
-   Production-ready only.
-   Keep MVP cost near ₹0.
-   Use free tiers where possible.
-   Update documentation every milestone.
-   Commit every completed milestone.

## Milestones

### M1 Repository Cleanup

-   Remove dead code
-   Remove backups
-   Remove **pycache**
-   Clean dependencies
-   Create .gitignore
-   Improve README
-   Lint
-   Fix imports

### M2 Architecture

-   Frontend/backend separation
-   API versioning
-   Environment configuration
-   Service layer
-   Repository pattern
-   Folder redesign

### M3 Database

-   PostgreSQL
-   Neon
-   SQLModel
-   Alembic
-   Relationships
-   Indexes
-   Constraints

### M4 Authentication

-   Registration
-   Login
-   Logout
-   JWT
-   Refresh Tokens
-   Email verification
-   Forgot password
-   Password reset
-   User profile

### M5 RBAC

Global Roles: - Customer - Platform Admin

Restaurant Roles: - Owner - Manager - Cashier - Waiter - Kitchen Staff

Features: - Permissions - Restaurant membership - Route protection -
Cross-tenant isolation

### M6 Restaurant Management

-   Restaurant CRUD
-   Restaurant profile
-   Staff management
-   Invitations
-   Ownership transfer
-   Logo
-   Cover image
-   Cloudinary integration

### M7 Menu Management

-   Categories
-   Menu items
-   Variants
-   Add-ons
-   Availability
-   Pricing
-   Images

### M8 Tables & QR

-   Tables
-   QR generation
-   QR validation
-   Invite links

### M9 Dining Sessions

-   Join session
-   Leader
-   Participants
-   Session lifecycle
-   Recovery

### M10 Shared Cart

-   Shared cart
-   Merge handling
-   Synchronization

### M11 Realtime

-   WebSockets
-   Live ordering
-   Presence
-   Cart sync

### M12 Kitchen Dashboard

-   Order queue
-   Preparation
-   Ready
-   Completed

### M13 Order Lifecycle

-   Status management
-   Cancellation
-   Refund workflow

### M14 Bill Split Engine

-   Equal split
-   Item split
-   Percentage split
-   Tax
-   Discount
-   Tips
-   Partial payment
-   Rounding

### M15 Payments

-   Razorpay
-   Verification
-   Webhooks
-   Settlement

### M16 Notifications

-   Email
-   Push
-   Realtime

### M17 Analytics

-   Revenue
-   Orders
-   Customer insights
-   Reports

### M18 Performance

-   Query optimization
-   Caching
-   Lazy loading
-   Bundle optimization

### M19 Security Audit

-   RBAC audit
-   Rate limiting
-   Validation
-   CORS
-   Secrets
-   Audit logs

### M20 Testing

-   pytest
-   Frontend tests
-   Integration tests
-   Load tests
-   CI/CD

### M21 Deployment

-   Vercel
-   Railway/Render
-   Neon
-   Cloudinary
-   Sentry
-   Production configuration

### M22 Production Audit

-   Code review
-   Security review
-   Scalability
-   Performance
-   Startup readiness

## Acceptance Criteria

Every milestone must end with: - Working feature - Tests passing -
Documentation updated - Git commit - Repository deployable - No
regressions
