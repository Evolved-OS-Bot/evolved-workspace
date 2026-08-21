# Website V2 Cloudflare Rollback Snapshot

**Date:** 4 August 2026  
**Mode:** Owner-authenticated, read-only  
**Status:** Captured; no Cloudflare setting changed  
**Zone:** `theevolvedgym.com.au`  
**Private source:** `data/private/website-migration-baselines/2026-08-04-cloudflare-read-only/theevolvedgym.com.au-zone-export.txt`  
**Source SHA-256:** `5985a2ca2a381e5d1d2b6382089f84071f4daf2b342dfa45de36a436b8ec0885`

## Outcome

The current Cloudflare DNS, proxy, redirect, Worker and SSL/TLS state is now
captured as rollback evidence for the Website V2 root-domain promotion.
Cloudflare exported 29 DNS records at provider timestamp
`2026-08-04 09:43:36`; the export does not state a timezone.

No DNS record, proxy state, rule, certificate, setting or account object was
created, edited, enabled, disabled or deleted.

## Critical Host Restore Values

These are the exact provider-side values to restore if a later approved
rehearsal or cutover changes the current web-routing records.

| Host | Type | Provider content | Proxy | TTL |
|---|---|---|---|---|
| `theevolvedgym.com.au` | A | `162.159.140.166` | Proxied | Auto |
| `www.theevolvedgym.com.au` | CNAME | `sites.ludicrous.cloud` | Proxied | Auto |
| `blog.theevolvedgym.com.au` | A | `35.213.240.236` | DNS only | Auto |
| `evolvedwoman.theevolvedgym.com.au` | A | `35.213.240.236` | DNS only | Auto |
| `evolved-woman.theevolvedgym.com.au` | CNAME | `host10.groovepages.com` | Proxied | Auto |
| `links.theevolvedgym.com.au` | CNAME | `brand.ludicrous.cloud` | DNS only | 1 hour |
| `trainers.theevolvedgym.com.au` | CNAME | `clientportal.ludicrous.cloud` | DNS only | 1 hour |
| `pay.theevolvedgym.com.au` | CNAME | `hosted-checkout.stripecdn.com` | DNS only | 5 minutes |
| `checkout.theevolvedgym.com.au` | CNAME | `get.groovesell.com` | Proxied | Auto |
| `education.theevolvedgym.com.au` | CNAME | `get.groovemember.net` | Proxied | Auto |
| `transformationflix.theevolvedgym.com.au` | CNAME | `get.groovemember.net` | Proxied | Auto |
| `email.mail.theevolvedgym.com.au` | CNAME | `mailgun.org` | DNS only | Auto |

There is no `go.theevolvedgym.com.au` A, AAAA or CNAME record.

The public root resolves to Cloudflare edge addresses, but those public answers
are not the rollback source. The provider-side A value above is the governed
restore value.

## Complete DNS Boundary

The export contains 29 records:

| Record type | Count |
|---|---:|
| A | 3 |
| CNAME | 9 |
| MX | 8 |
| TXT | 9 |

### Mail routing

| Host | Priority | Target | TTL |
|---|---:|---|---:|
| `mail.theevolvedgym.com.au` | 10 | `mxa.mailgun.org` | 600 |
| `mail.theevolvedgym.com.au` | 20 | `mxb.mailgun.org` | 600 |
| `send.theevolvedgym.com.au` | 10 | `feedback-smtp.ap-northeast-1.amazonses.com` | 3600 |
| `theevolvedgym.com.au` | 1 | `aspmx.l.google.com` | Auto |
| `theevolvedgym.com.au` | 5 | `alt1.aspmx.l.google.com` | Auto |
| `theevolvedgym.com.au` | 5 | `alt2.aspmx.l.google.com` | Auto |
| `theevolvedgym.com.au` | 10 | `aspmx2.googlemail.com` | Auto |
| `theevolvedgym.com.au` | 10 | `aspmx3.googlemail.com` | Auto |

The nine TXT records cover Stripe certificate validation, DMARC, Mailgun DKIM
and SPF, Resend DKIM, Amazon SES SPF, Groove verification and two Google site
verifications. Their exact values remain in the protected zone export and
must be restored from that file rather than retyped from this share-safe
summary.

The authoritative nameservers are `jim.ns.cloudflare.com` and
`zariyah.ns.cloudflare.com`. DNS setup is `Full`; DNSSEC is disabled.

## Redirect and Request-Handling State

### Zone rules

Cloudflare reports:

- zero Redirect Rules;
- zero URL Rewrite Rules;
- zero Configuration Rules;
- zero Origin Rules;
- zero request-header or response-header transform rules;
- zero Cache Rules or Cache Response Rules;
- zero Compression Rules; and
- zero legacy Page Rules.

There are no Workers routes configured for the zone. Cloudflare Snippets are
not active on the current Free plan.

### Account-level bulk redirect

One enabled rule, `Logo Redirect`, references the active list
`logoredirects`. The list contains eight permanent 301 redirects:

| Source | Target |
|---|---|
| `https://www.theevolvedgym.com.au/beth.png` | `https://pub-21c388a877d8484db98b3c1288b2915c.r2.dev/Beth.png` |
| `https://www.theevolvedgym.com.au/hannah.png` | `https://pub-21c388a877d8484db98b3c1288b2915c.r2.dev/Hannah.png` |
| `https://www.theevolvedgym.com.au/leisa.png` | `https://pub-21c388a877d8484db98b3c1288b2915c.r2.dev/Leisa.png` |
| `https://www.theevolvedgym.com.au/logo.png` | `https://pub-21c388a877d8484db98b3c1288b2915c.r2.dev/Logo.png` |
| `https://www.theevolvedgym.com.au/marnie.png` | `https://pub-21c388a877d8484db98b3c1288b2915c.r2.dev/Marnie.png` |
| `https://www.theevolvedgym.com.au/megan.png` | `https://pub-21c388a877d8484db98b3c1288b2915c.r2.dev/Megan.png` |
| `https://www.theevolvedgym.com.au/ogimage.png` | `https://pub-21c388a877d8484db98b3c1288b2915c.r2.dev/ogimage.png` |
| `https://www.theevolvedgym.com.au/piper.png` | `https://pub-21c388a877d8484db98b3c1288b2915c.r2.dev/Piper.png` |

This existing rule and list are outside the new root-promotion redirect set.
They must remain unchanged unless separately reviewed and approved.

## SSL/TLS State

| Setting | Current value |
|---|---|
| Encryption mode | Full (strict), Automatic mode enabled |
| Universal certificate | Active for `*.theevolvedgym.com.au` and apex; managed expiry 8 October 2026 |
| Backup certificate | Issued; managed expiry 10 September 2026 |
| Always Use HTTPS | Enabled |
| HSTS | Disabled |
| Minimum TLS | TLS 1.0 default |
| Opportunistic Encryption | Enabled |
| TLS 1.3 | Enabled |
| Automatic HTTPS Rewrites | Enabled |
| Certificate Transparency Monitoring | Disabled |

## Rollback Use

For a later approved root-host rehearsal or cutover:

1. take a new export immediately before any Cloudflare mutation;
2. retain this snapshot as the 4 August comparison point;
3. restore the exact root and `www` provider values and proxy states above if
   rollback is triggered;
4. leave `blog`, `links`, mail, verification, legacy hosts and the existing
   `Logo Redirect` rule untouched unless the approved change set explicitly
   includes them;
5. restore the captured SSL/TLS states if any of them changed; and
6. verify the GHL root, the Website V2 `blog.` runtime, mail DNS, `links.` and
   the eight image redirects after rollback.

This capture resolves the Phase 3 owner-authentication evidence gap. It does
not authorise the additive `go.` record, the isolated rehearsal or the live
root cutover.
