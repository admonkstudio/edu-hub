# Edu Hub Product Architecture

## Product model

Edu Hub combines two Phase 1 products:

1. **Education Directory** — structured institution/entity data.
2. **Education Knowledge Platform** — editorial guidance connected to directory entities and taxonomies.

The two systems should reinforce each other through shared entities, locations, curricula, programs, topics, and internal links.

## Core entity model

Do not flatten the product into one `schools` table.

```text
Provider / organization
  └── Institution
       ├── Campus / branch
       ├── Education levels
       ├── Curricula
       ├── Certificates
       ├── Languages
       ├── Accreditations
       ├── Admissions
       └── Fees

Higher-education institution
  ├── Campus
  ├── Academic unit
  │    └── Academic unit
  └── Program
```

### First-class institution families

- nursery / preschool
- school
- university
- higher institute
- academy where relevant
- technological institution
- foreign university branch

Attributes such as British, American, IB, private, public, girls, boys, international, etc. should be modeled as dimensions/relationships where appropriate rather than baked into top-level entity types.

## Geography

Use controlled hierarchical geography:

```text
Country
→ Governorate
→ City
→ District
→ Area / neighborhood
→ Campus
```

Location must support future map/radius search and deliberate location landing pages.

## Trust model

Keep these independent:

### Data status

Candidate → researching → sourced → reviewed → officially sourced / institution confirmed, with conflicting/stale/disputed states where needed.

### Claim status

Unclaimed → claim requested → verification pending → claimed → suspended.

### Commercial status

Free → future premium/sponsored/partner states.

Commercial status must never make a factual claim verified.

## Freshness

Not every field has the same review cadence.

High-volatility examples:

- admissions deadlines
- fees
- application URLs
- phone/email

Medium-volatility examples:

- programs
- curricula
- accreditation
- facilities

Low-volatility examples:

- foundation year
- historical facts

The research/admin system should generate review work based on field/entity freshness rather than forcing complete monthly re-research of every institution.

## Content model

Editorial content should connect to structured entities.

Core content types:

- article
- guide
- comparison
- explainer
- report
- relevant education news

Initial topic families:

- choosing education
- curricula and systems
- admissions
- fees and costs
- parent guides
- student guides
- universities
- programs and careers
- exams
- education policy/developments
- scholarships
- special education

## Phase 1 user journeys

### Find

Find a school, nursery, university, institute, program, or location.

### Filter

Narrow by useful structured attributes.

### Understand

Read explanatory content about curricula, admissions, fees, education systems and decisions.

### Decide

Use profile details and later comparison capabilities to evaluate options.

## Phase 2-ready but not Phase 1 implementation

Architectural decisions should not block future:

- claimed listings
- institution change requests
- premium profile features
- enquiries/leads
- applications
- advertising/sponsorship
- institution analytics

Do not implement these until later approved scope.
