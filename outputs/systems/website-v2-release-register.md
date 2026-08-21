# Website V2 Release Register

**Product:** Evolved Website V2  
**Canonical manifest:** `outputs/systems/website-v2-release-manifest.md`  
**Rule:** Append verified releases. Do not rewrite an earlier release entry to
make later production state appear historical.

## Release Evidence Contract

Every entry must record:

- release or capture date;
- production URL and WordPress homepage ID;
- verified H1, CTA and homepage asset version;
- clean source-mirror location and hashes;
- protected recovery point;
- live read-back performed;
- systems deliberately unchanged; and
- known drift, exceptions or follow-up.

## 2026-08-04: V2 Identity Recovery and Governed Baseline

**Classification:** Documentation and source-control recovery; no live release  
**Runtime:** `https://blog.theevolvedgym.com.au/`  
**Homepage:** WordPress post ID 165  
**Live H1:** `Brisbane's Leading Women-Only Gym`  
**Live primary CTA:** `Join the Waitlist`  
**Live homepage JavaScript:** `homepage.js?ver=59.0`  
**Conversion authority:** `reference/conversion-funnel.md`

### Evidence

- Browser inspection on 4 August verified the V2 homepage, 17-section
  experience, personalised results curve, member/results content,
  memberships, timetable, reviews, FAQ and waitlist journey.
- The read-only live drift check returned HTTP 200, verified the governed H1,
  waitlist CTA and `59.0` asset version, and proved the live `homepage.js`
  bytes match the governed source-mirror hash.
- The Phase 1 production capture from 3 August contains the complete WordPress
  filesystem, SQL database, 11,655 production-file hashes and browser
  verification for 61 HTML routes.
- The complete deployed Blocksy child theme and post-165 homepage HTML were
  copied byte-for-byte from that protected capture into
  `wordpress/website-v2/source/`.
- `wordpress/website-v2/SOURCE_SHA256SUMS.txt` records the governed clean-source
  hashes.

### Known Transfer-Readiness Issues

- the root domain still serves the older GHL site;
- `go.theevolvedgym.com.au` was not working at the Phase 1 snapshot;
- the V2 `/blog` footer target and old
  `/terms-of-use-and-privacy-policy` target fail;
- WordPress URL and media references still reflect the pre-cutover blog
  hostname;
- root-domain, redirect, form, asset, SSL and rollback rehearsal remains; and
- the content and SEO backlog remains preserved separately from the
  root-promotion gate.

### Unchanged Systems

No WordPress production content, GHL asset, DNS record, redirect, Git stage,
commit or branch was changed by this governance correction.
