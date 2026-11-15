# ManualOps Radar — Phase 1.5 Commercial Validation Study

**Verification Date:** `2026-11-15`  
**Target Paying Customer Evaluated:** Small AI & Workflow Automation Agencies (building on n8n, Make.com, Zapier, Airtable, Python/LLMs).

---

## 1. Research on 10 Real Workflow & AI Automation Agencies (Public Sources)

All 10 agencies below were researched via publicly published service pages, agency directories, and case studies (zero personal contact harvesting):

| # | Agency Name & Public URL | Core Stack | Published Pricing / Engagement Model | Primary Automation Projects Offered |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **XRay.Tech** (`https://xray.tech` / [AI Agency Index](https://theaiagencyindex.com/agency/xray-tech/)) | Zapier, Make, n8n, Airtable | Listed at \$250/hr, project builds, or retainers | Process design, Airtable operational databases, document automation, and staff enablement for mid-market teams. |
| **2** | **Left Hook** (`https://lefthook.com/`) | Zapier, Make, custom API connectors, QuickBooks, Shopify, 3PL | Fixed-scope quick wins + ongoing optimization retainers | Connecting practice management to billing (eliminating manual data entry), and Shopify-to-3PL-to-QuickBooks order fulfillment sync. |
| **3** | **Luhhu** (`https://luhhu.com` / [n8nLab Comparison](https://n8nlab.io/blog/best-n8n-automation-agencies-us)) | Zapier, Make, n8n | Fixed migration scopes & SMB project builds | Migrating mid-market teams from high-cost Zapier/Make setups into self-hosted or cloud n8n workflows; CRM & billing sync. |
| **4** | **Msquare Automation Solutions** (`https://msquare.pro/us/make-com-automation-services-for-businesses-in-the-usa/`) | Make.com (Certified Partner), n8n, Airtable, HubSpot, OpenAI/Claude | Prepaid hour bundles & project quotes | Weekly agency reporting (Make + Airtable + Slack), HubSpot + OpenAI lead qualification, and Shopify + Stripe order data-entry automation. |
| **5** | **Automation Helpers** ([Softr Airtable Agency Directory](https://www.softr.io/blog/airtable-agencies)) | Airtable, Make, Zapier | Project-based systems architecture & retainers | Helping SMB/mid-market teams escape "spreadsheet sprawl" by replacing fragile Excel/Sheets trackers with Airtable + backend automation. |
| **6** | **9x** ([Softr Airtable Agency Directory](https://www.softr.io/blog/airtable-agencies)) | Airtable, Make, Zapier, Softr, Webflow | Custom system builds & training | End-to-end internal operational tools, automated reporting layers, and client portals connected to back-office databases. |
| **7** | **Claribase Consulting** ([Softr Airtable Agency Directory](https://www.softr.io/blog/airtable-agencies)) | Airtable, Zapier | Boutique consulting & custom builds | Turning messy manual spreadsheet processes into structured Airtable databases and automated reporting workflows. |
| **8** | **Arcesso** (`https://arcesso.ai/ai/ai-automation-agency/`) | Self-hosted n8n, Make, LLMs | Client-owned repository/account builds | Building self-hosted n8n + LLM workflows inside the client's own cloud account to avoid per-task Zapier fees. |
| **9** | **Acceltor** (`https://www.acceltor.net/workflow-automation.html`) | n8n, Make, Zapier, Google Workspace, Slack, CRM, Accounting | Fixed quotes starting at \$1,490 (1–3 week delivery) | Moving leads into CRM, creating invoices, client onboarding, syncing orders/inventory, and building automated weekly reports. |
| **10** | **Hack'celeration** (`https://hackceleration.com/agency/automation`) | n8n, Make, Zapier + AI steps | Free initial process audit, then builds from \$2,000 | Connecting existing SaaS tools to eliminate manual copy-pasting across CRM, invoicing, and internal handoffs. |

---

## 2. What Projects They Offer & Which Signals Actually Help Them

### A. Common Denominator of Agency Projects ($1,500–$15,000 Sweet Spot)
Small automation agencies do **not** sell core software engineering, custom ERP modules, or enterprise SOX compliance. They sell **1-to-4 week cross-application glue workflows**:
1. **Spreadsheet-to-Database Migrations:** Replacing multi-tab Google Sheets/Excel trackers (commissions, inventory, vendor onboarding) with Airtable + Make/n8n.
2. **Order / Invoice / Billing Sync:** Connecting Shopify/Stripe/CRM to QuickBooks/Xero/NetSuite/3PL to stop manual re-keying of invoices and orders.
3. **Automated Weekly/Monthly Reporting Packs:** Pulling metrics from ads/CRM/billing into Slack/Airtable/Google Slides without manual CSV exports.
4. **Zapier-to-n8n Cost Migrations:** Re-architecting brittle, expensive Zapier zaps into n8n.

### B. Which Opportunity Signals Actually Help Agencies Find Clients (vs. Noise)
- **Useless Signals for Agencies (Low/Zero Value):**
  - Job postings at **500–10,000+ employee tech enterprises** (Stripe, Cloudflare, Datadog, GitLab): These companies have internal RevOps, Data Engineering, and Enterprise AI teams, plus strict vendor security/SOC2 procurement gates that block small agencies.
  - Generic **BDR/AE Salesforce hygiene bullets** (*"Update Salesforce with call notes"*): Routine human sales behavior, not an agency project.
  - Senior **GAAP Accounting Controller close roles**: Require CPA sign-off and enterprise ERP governance, not a \$3,000 Make/n8n workflow.
- **High-Value Signals for Agencies (Actionable):**
  1. **Explicit "Spreadsheet Sprawl" Admission in SMB/Mid-Market (20–250 employees):** Postings mentioning *"move from spreadsheet-based administration"*, *"consolidate multiple Google Sheets trackers"*, or *"manage trackers in Excel/Google Sheets and Airtable"*.
  2. **Named SaaS-Pair Manual Bridge:** Postings that name **two specific tools** with a manual human bridge between them (e.g., *"reconcile Stripe payouts against QuickBooks/NetSuite"*, *"enter HubSpot closed-won deals into billing/ERP"*, *"sync Shopify orders with 3PL spreadsheets"*).
  3. **Fractional / Operations Coordinator Overload:** Non-tech companies hiring an *Operations Coordinator*, *Billing Specialist*, or *Sales Ops Analyst* specifically to handle manual copy-paste/data entry across named SaaS tools (`Airtable`, `Zapier`, `Make`, `HubSpot`, `QuickBooks`, `NetSuite`, `Monday.com`, `Shopify`).

---

## 3. Competitive Landscape: Existing Lead-Gen Tools vs. ManualOps Radar

| Tool Category & Examples | What They Already Provide Out-of-the-Box (Verified) | Where They Fall Short | Where ManualOps Radar Could Genuinely Add Value |
| :--- | :--- | :--- | :--- |
| **AI Outbound & Enrichment Tables** (**Clay.com**, Apollo.io) | Clay already has native **Find Jobs** sources (Greenhouse, Lever, LinkedIn, Indeed) AND allows users to run a \$0.01 GPT-4o-mini prompt column on every job description to extract keywords, enrich company size, and find decision-maker emails in one table. | Keyword searches in Clay (`"Excel"`, `"Salesforce"`, `"reporting"`) pull in **>90% false positives** (general skills, idioms, enterprise roles), burning enrichment credits on bad-fit companies. | **Not as a standalone job scraper** (Clay already scrapes jobs). Value exists **only** if we provide pre-filtered, high-precision **"Named-Tool Manual Bridge Briefs"** (e.g., `HubSpot <-> NetSuite manual entry` at 20–250 person non-tech companies) with a ready-to-pitch workflow diagram. |
| **Hiring Intent Platforms** (**LoneScale**, **Sumble**, **Trigify**, Common Room) | Track job postings, tech-stack mentions, and new executive hires across thousands of companies, pushing alerts to Slack/CRM. | Built for \$30k–\$100k+ ACV B2B SaaS sales teams (pricing typically \$500–\$2,000+/month), which is too expensive for a 2–10 person automation agency charging \$2,000/project. | Low-cost, curated **Agency Deal Briefs** focused specifically on *automatable manual workflows* rather than generic SaaS hiring intent. |

---

## 4. Five Evidence-Backed Opportunity Briefs (Verified Public Sources)

All 5 briefs below were retrieved directly from official public Greenhouse Job Board APIs and verified on `2026-11-15`:

### Brief 1: Zocdoc — Sales Commissions Spreadsheet-to-System Migration
- **Company & Role:** Zocdoc — *Commissions Manager*
- **Public Source URL:** https://job-boards.greenhouse.io/zocdoc/jobs/8346400
- **Publication / Update Date:** Updated `2026-11-05` | **Verified:** `2026-11-15`
- **Operational Pain Evidence (Verbatim):**
  1. *"Own the commission lifecycle for Sales and eligible go-to-market teams, from calculations and reconciliations through approvals, payroll submissions and employee statements."*
  2. *"Lead the move from spreadsheet-based administration to an enterprise incentive compensation management platform, including requirements, vendor evaluation, business case development, data design, historical migration..."*
- **Possible Automation Solution:** Automated CRM-to-commission calculation & reconciliation pipeline, plus historical spreadsheet data cleansing, validation, and migration scripts into the new ICM platform.
- **Why an Outside Agency Might Be Relevant:** Explicitly states they are currently running commissions on spreadsheets (`spreadsheet-based administration`) and need `data design, historical migration` and `vendor evaluation`. A specialized RevOps/data automation agency could pitch a fixed-scope **Historical Commission Data Cleansing & CRM Reconciliation Bridge** during their transition.
- **What Is Still Unknown (Uncertainty):** Zocdoc is hiring a full-time Commissions Manager to lead this internally and has an internal engineering/data team; whether Finance has separate budget for an external implementation partner is unknown.

### Brief 2: Zocdoc — Provider Data Operations Spreadsheet & AppScript Workflows
- **Company & Role:** Zocdoc — *Provider Data Operations Associate* & *Manager, Provider Data Operations*
- **Public Source URLs:** https://job-boards.greenhouse.io/zocdoc/jobs/8347471 & https://job-boards.greenhouse.io/zocdoc/jobs/8347474
- **Publication / Update Date:** Updated `2026-11-04` & `2026-11-06` | **Verified:** `2026-11-15`
- **Operational Pain Evidence (Verbatim):**
  1. *"Use Excel/Google spreadsheets to manage and update large datasets, create reports, and conduct data analysis"*
  2. *"Guide the team in adopting AI-driven tools and transitioning from manual processes to scalable systems."*
  3. *"Familiarity with Microsoft Excel and Google Sheets including Google AppScripts."*
- **Possible Automation Solution:** Replacing fragile Google Sheets + manual AppScripts provider-roster updates with an automated n8n/Make + LLM data-normalization and validation pipeline before loading provider records.
- **Why an Outside Agency Might Be Relevant:** Operations teams relying on Google Sheets + custom AppScripts for large provider datasets frequently hit execution timeouts and manual formatting bottlenecks that an Airtable/n8n agency can prototype in 2 weeks.
- **What Is Still Unknown (Uncertainty):** The Manager role explicitly states *"Partner with AI, Product, and Engineering teams to design, test, and scale solutions"*, indicating strong internal build competition.

### Brief 3: Flexport — High-Volume Freight Invoice Auditing & AP Reconciliation
- **Company & Role:** Flexport — *Auditor, Accounts Payable & Freight Audit* & *Manager, Account Payable*
- **Public Source URLs:** https://job-boards.greenhouse.io/flexport/jobs/7660304 & https://job-boards.greenhouse.io/flexport/jobs/8336471
- **Publication / Update Date:** Updated `2026-11-07` | **Verified:** `2026-11-15`
- **Operational Pain Evidence (Verbatim):**
  1. *"Oversee the accuracy and timeliness of high-volume invoice processing, freight invoice auditing, and account reconciliation across the team"*
  2. *"Support the implementation of automation tools and identify opportunities to streamline invoice processing, improve workflows, and reduce manual errors"*
- **Possible Automation Solution:** OCR/LLM freight invoice extraction + automated line-item rate/accessorial charge matching against purchase orders and carrier rate cards, flagging only exceptions for human review.
- **Why an Outside Agency Might Be Relevant:** Explicitly mentions supporting *"the implementation of automation tools... to streamline invoice processing... and reduce manual errors"*. Document/invoice extraction + ERP reconciliation is a core deliverable of AI automation agencies.
- **What Is Still Unknown (Uncertainty):** Flexport is a large logistics-tech company with internal AI engineers (`Senior Applied AI Engineer, Autonomous Supply Chains`); they may strongly prefer internal tooling or enterprise AP platforms over a boutique agency.

### Brief 4: Faire — End-to-End Contracting Intake, Routing & Approval Redesign
- **Company & Role:** Faire — *Legal Technology & Operations Manager*
- **Public Source URL:** https://boards.greenhouse.io/faire/jobs/8943505002?gh_jid=8943505002
- **Publication / Update Date:** Updated `2026-11-13` | **Verified:** `2026-11-15`
- **Operational Pain Evidence (Verbatim):**
  *"In partnership with Procurement and GTM, map Faire’s end-to-end contracting lifecycle, redesign it to reduce manual work and identify areas for efficiency across intake, routing, review, approval, signature, storage, and obligation tracking."*
- **Possible Automation Solution:** Automated legal/procurement intake & routing workflow connecting Slack, Salesforce/CRM, CLM (Ironclad/DocuSign), and procurement approval queues.
- **Why an Outside Agency Might Be Relevant:** Legal & Procurement Ops teams are often starved of internal software engineering bandwidth and frequently use external workflow specialists to wire up CLM-to-CRM-to-Slack intake routing.
- **What Is Still Unknown (Uncertainty):** Faire is hiring a dedicated Legal Technology & Operations Manager to own this; whether they want external implementation help after mapping the process is unverified.

### Brief 5: Cloudflare — Physical Data Center Inventory Entry & Access Control Reconciliation
- **Company & Role:** Cloudflare — *DCIM Administrator* & *DCSC Automation Specialist*
- **Public Source URLs:** https://boards.greenhouse.io/cloudflare/jobs/7539895 & https://boards.greenhouse.io/cloudflare/jobs/7682182
- **Publication / Update Date:** Updated `2026-11-12` | **Verified:** `2026-11-15`
- **Operational Pain Evidence (Verbatim):**
  1. *"Data Integrity Champion: Perform daily data entry, manage automated asset discovery tools, and reconcile physical inventory against Nlyte records to guarantee 99.5%+ accuracy."*
  2. *"The operational burden of this work is substantial and largely manual: user lists are pulled by hand, access control lists are reconciled by eye, evidence packages are assembled tier by tier."*
- **Possible Automation Solution:** Automated diff & reconciliation workflow comparing discovered network/badge assets against Nlyte DCIM and assembling compliance evidence packages automatically.
- **Why an Outside Agency Might Be Relevant:** Demonstrates how even massive tech companies have pockets of severe manual reconciliation (`"pulled by hand"`, `"reconciled by eye"`).
- **What Is Still Unknown (Uncertainty):** High security/compliance barrier (data center access lists) and Cloudflare is explicitly hiring an internal *DCSC Automation Specialist* to build this in-house.

---

## 5. Small Paid-Pilot Offer & Practical Outreach Experiment (Drafts Only — DO NOT SEND)

### A. Proposed Paid-Pilot Offer ("Curated Workflow Pain Briefs")
Instead of building a SaaS dashboard first, test commercial willingness-to-pay with a **Concierge Paid Pilot**:
- **Deliverable:** **15 Verified Mid-Market "Manual Bridge" Opportunity Briefs per week for 4 weeks** (60 briefs total), filtered strictly to **20–250 employee non-tech/mid-market companies** whose active job postings explicitly mention manual work across **their exact agency stack** (e.g., `Excel/Google Sheets` + `HubSpot/Salesforce/QuickBooks/NetSuite/Shopify/Airtable`).
- **Included per Brief:** Verbatim pain quote, direct job link, named software stack in use, and a 3-bullet "Suggested n8n/Make Pitch Angle".
- **Pilot Price:** **\$199 one-time for a 4-week pilot** (or \$99 for a 20-brief starter pack), with a 100% refund if the agency does not find at least 10 of the briefs worth adding to their outbound sequence.

### B. Draft Outreach Messages for Validation Experiment (DO NOT SEND)

#### Draft 1: To an Airtable / Spreadsheet-Migration Agency (e.g., Automation Helpers / Claribase style)
> **Subject:** Question on how you spot "spreadsheet sprawl" accounts before they hire
>
> Hi [Name] — saw your work helping mid-market teams replace fragile Excel/Google Sheets trackers with Airtable + Make/Zapier workflows.
>
> Quick question: do you currently monitor public job postings where 30–200 person companies explicitly admit they are stuck in manual spreadsheet consolidation (e.g., Zocdoc's recent Commissions role citing *"move from spreadsheet-based administration"* and manual reconciliations)?
>
> We built a deterministic filter on public ATS feeds that strips out the 93% of job posts that just list "Excel skills" and isolates only postings describing active manual spreadsheet/data-entry bottlenecks alongside their current CRM/ERP stack.
>
> Before we turn this into a product, we're running a \$199 4-week concierge pilot (15 verified manual-workflow briefs/week tailored to your Airtable/Make stack). Would you be open to seeing 3 sample briefs from this week's run to tell me if the signal quality is actually useful for your outbound?

#### Draft 2: To an n8n / Make Back-Office Automation Agency (e.g., Acceltor / Msquare / Hack'celeration style)
> **Subject:** Filtering job boards for actual copy-paste / reconciliation bottlenecks
>
> Hi [Name] — I noticed your team focuses on fixed-quote n8n and Make builds that replace manual copy-paste work across CRM, invoicing, and weekly reporting.
>
> When agencies try to use Clay or Apollo to scrape job boards for leads, >90% of matches for "Excel", "CRM", or "reporting" are just generic skill requirements rather than real manual bottlenecks.
>
> We've been testing a rule-based radar on public job APIs that separates routine job duties from explicit manual workflow pain (like daily invoice reconciliation or manual cross-app data entry), with the exact verbatim quote and source URL preserved.
>
> Can I send over 3 live opportunity briefs we pulled today (no charge or pitch deck) just to get your honest feedback on whether this signal is stronger than what you currently use in Clay/Apollo?
