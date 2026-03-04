# iHhashi Legal Documents - Implementation Guide

## Overview

This directory contains all legal documents required for iHhashi's operation in South Africa, fully compliant with:
- **POPIA** (Protection of Personal Information Act 4 of 2013)
- **CPA** (Consumer Protection Act 68 of 2008)
- **ECT Act** (Electronic Communications and Transactions Act 25 of 2002)

---

## Documents Created

### 1. PRIVACY_POLICY.md
**URL:** https://ihhashi.co.za/privacy

**Key Features:**
- POPIA compliant structure
- Data subject rights clearly outlined
- 17 comprehensive sections
- Cookie policy reference
- Contact details for Information Regulator
- Data retention schedules

**Critical Sections:**
- Section 2: Information We Collect
- Section 5: How We Use Your Information
- Section 9: Your Rights Under POPIA
- Section 10: Exercising Your Rights

**Word Count:** ~4,500 words

---

### 2. TERMS_OF_SERVICE.md
**URL:** https://ihhashi.co.za/terms

**Key Features:**
- Comprehensive service description
- Three-way relationship (Platform-Customer-Partner-Merchant)
- Independent contractor status clearly defined
- Pricing model explanation (base + partner fee + customer choice)
- CPA cooling-off rights included

**Critical Sections:**
- Section 2.4: Pricing Model (inDriver-style)
- Section 5: Delivery Partner Terms (Independent Contractor)
- Section 10: Dispute Resolution (South African jurisdiction)
- Section 11: Consumer Protection Act Compliance

**Word Count:** ~5,800 words

---

### 3. DELIVERY_PARTNER_AGREEMENT.md
**URL:** https://ihhashi.co.za/partner-agreement

**Key Features:**
- Detailed independent contractor agreement
- Fee-setting freedom clearly articulated
- 45-day free trial terms
- Service standards and metrics
- Vehicle requirements by transport type
- Blue Horse verification program

**Critical Sections:**
- Section 2: Independent Contractor Relationship
- Section 3.1: Fee-Setting Freedom
- Section 3.2: Customer Choice Model
- Section 5.1: Order Acceptance Process

**Word Count:** ~5,700 words

---

### 4. CUSTOMER_TERMS.md
**URL:** https://ihhashi.co.za/customer-terms

**Key Features:**
- Customer-specific terms
- Order process explanation
- Pricing transparency
- Refund and cancellation policy
- CPA cooling-off rights (5 days)
- Age restrictions (18+ for alcohol)

**Critical Sections:**
- Section 3: Placing Orders (including partner selection)
- Section 4: Pricing and Payment
- Section 6: Cancellations and Refunds
- Section 6.6: CPA Cooling-Off Right

**Word Count:** ~4,900 words

---

### 5. COOKIE_POLICY.md
**URL:** https://ihhashi.co.za/cookies

**Key Features:**
- Detailed cookie categorization
- POPIA lawful processing basis
- Browser-specific management instructions
- Third-party cookie disclosure
- Analytics and marketing cookie tables

**Critical Sections:**
- Section 3: Types of Cookies We Use (4 categories)
- Section 5: Managing Your Cookie Preferences
- Section 6: Cookies and POPIA Compliance

**Word Count:** ~4,200 words

---

## Total Legal Coverage

| Metric | Value |
|--------|-------|
| Total Word Count | ~25,000+ words |
| Pages (A4, 12pt) | ~50-60 pages |
| Legal Acts Referenced | 5+ |
| User Types Covered | 3 (Customer, Partner, Merchant) |
| Data Subject Rights | 8 (POPIA compliant) |

---

## Implementation Checklist

### Phase 1: Website Setup (Week 1)

- [ ] Create `/privacy` page - host PRIVACY_POLICY.md
- [ ] Create `/terms` page - host TERMS_OF_SERVICE.md
- [ ] Create `/partner-agreement` page - host DELIVERY_PARTNER_AGREEMENT.md
- [ ] Create `/customer-terms` page - host CUSTOMER_TERMS.md
- [ ] Create `/cookies` page - host COOKIE_POLICY.md

### Phase 2: Link Integration (Week 1)

- [ ] Footer links on all pages:
  ```
  Privacy Policy | Terms of Service | Cookie Policy | Partner Agreement
  ```

- [ ] Sign-up flows:
  - Customer registration: Link to Customer Terms
  - Partner registration: Link to Partner Agreement
  - Both: Link to Privacy Policy and Terms of Service

- [ ] Checkout process:
  - Checkbox: "I agree to the Terms of Service and Privacy Policy"
  - Link to Customer Terms

- [ ] Cookie consent banner:
  - Link to Cookie Policy
  - Accept/Reject/Customize options

### Phase 3: App Integration (Week 2)

- [ ] In-app legal section:
  - Settings → Legal
  - All 5 documents accessible
  - Download as PDF option

- [ ] Registration screens:
  - Checkbox with links to terms
  - Scrollable terms before acceptance

- [ ] Order confirmation:
  - Short summary of key terms
  - Link to full Customer Terms

### Phase 4: Email Templates (Week 2)

- [ ] Welcome email (Customers):
  - Summary of Customer Terms
  - Link to full terms

- [ ] Welcome email (Partners):
  - Summary of Partner Agreement
  - Fee structure reminder
  - Link to full agreement

- [ ] Order confirmation email:
  - Cancellation policy summary
  - Link to Customer Terms

---

## Technical Requirements

### Static Page Hosting

```
ihhashi.co.za/
├── privacy/              → PRIVACY_POLICY.md (HTML)
├── terms/                → TERMS_OF_SERVICE.md (HTML)
├── partner-agreement/    → DELIVERY_PARTNER_AGREEMENT.md (HTML)
├── customer-terms/       → CUSTOMER_TERMS.md (HTML)
├── cookies/              → COOKIE_POLICY.md (HTML)
└── legal/                → PDF versions for download
    ├── privacy-policy.pdf
    ├── terms-of-service.pdf
    ├── partner-agreement.pdf
    ├── customer-terms.pdf
    └── cookie-policy.pdf
```

### HTML Conversion

Convert Markdown to HTML with:
- Proper heading hierarchy (H1 → H2 → H3)
- Anchor links for sections
- Responsive tables
- Print-friendly CSS
- PDF download button

### SEO Meta Tags

```html
<!-- Privacy Policy -->
<title>Privacy Policy | iHhashi - Food Delivery South Africa</title>
<meta name="description" content="iHhashi's Privacy Policy - How we collect, use, and protect your personal information. POPIA compliant.">

<!-- Terms of Service -->
<title>Terms of Service | iHhashi</title>
<meta name="description" content="Terms of Service for iHhashi delivery platform. Customer, partner, and merchant terms.">
```

---

## Compliance Verification

### POPIA Compliance Check

| Requirement | Status | Document |
|-------------|--------|----------|
| Data subject rights | ✅ | Privacy Policy Section 9 |
| Lawful processing basis | ✅ | Privacy Policy Section 4 |
| Information Officer details | ⚠️ | Add to Privacy Policy |
| Data retention periods | ✅ | Privacy Policy Section 8 |
| Cross-border transfers | ✅ | Privacy Policy Section 6.3 |
| Consent mechanisms | ✅ | Cookie Policy |
| Breach notification | ✅ | Privacy Policy Section 7 |

### CPA Compliance Check

| Requirement | Status | Document |
|-------------|--------|----------|
| Cooling-off period (5 days) | ✅ | Customer Terms Section 6.6 |
| Price transparency | ✅ | All pricing documents |
| Refund policy | ✅ | Customer Terms Section 6 |
| Liability limitations | ✅ | Terms of Service Section 8 |
| Dispute resolution | ✅ | Terms of Service Section 10 |
| No unfair terms | ✅ | Reviewed throughout |

### ECT Act Compliance Check

| Requirement | Status | Document |
|-------------|--------|----------|
| Electronic contract formation | ✅ | Registration flows |
| Authentication | ✅ | SMS verification |
| Record retention | ✅ | Section 7 of all docs |
| Time and place of receipt | ✅ | Order confirmation system |

---

## Contact Information to Update

Before going live, update these placeholders:

### Privacy Policy
- [ ] Physical Address (Section 16)
- [ ] Information Officer name
- [ ] Deputy Information Officer name

### Terms of Service
- [ ] Physical Address (Section 14)
- [ ] Support phone number
- [ ] Company registration number

### Partner Agreement
- [ ] Company registration number
- [ ] Physical address for legal notices
- [ ] Partner support phone number

### All Documents
- [ ] Support email addresses (currently @ihhashi.co.za)
- [ ] Phone numbers
- [ ] Physical addresses

---

## Maintenance Schedule

### Quarterly Reviews
- Review for legal updates
- Check POPIA guidance changes
- Update data retention periods if needed

### Annual Reviews
- Full legal audit
- Update cookie lists
- Review third-party processors
- Refresh contact information

### Trigger-Based Updates
- New features requiring data collection
- New third-party integrations
- Changes to pricing model
- Expansion to new regions

---

## Next Steps

1. **Legal Review** (Recommended)
   - Have a South African attorney review all documents
   - Verify compliance with latest regulations
   - Check industry-specific requirements

2. **Translation** (Future)
   - Translate into isiZulu, Sesotho, Afrikaans
   - Ensure legal accuracy in translations
   - Make language selector available

3. **PDF Generation**
   - Create downloadable PDF versions
   - Include version numbers and dates
   - Add official company letterhead

4. **User Testing**
   - Test readability with actual users
   - Verify all links work
   - Check mobile display

---

## Document Version Control

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0 | 2026-03-01 | Initial release | [Name] |

---

## Questions?

For questions about these legal documents:
- **Technical:** support@ihhashi.co.za
- **Legal:** legal@ihhashi.co.za
- **Privacy:** privacy@ihhashi.co.za

---

**© 2026 iHhashi (Pty) Ltd. All rights reserved.**

**Disclaimer:** These documents are provided as templates. While they are drafted to comply with South African law, we strongly recommend having them reviewed by a qualified attorney before use in production.
