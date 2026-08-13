# Problem statement: recognizing the same person again

## 1. The problem

Some services need to recognize the same verified person again for one stated use. Login alone cannot do this across accounts or credentials, before signup, or after account access is lost. Every one-per-person rule must recognize a repeat, even when rejecting it; a changing rule must find or carry forward the person's state.

The question is: for this service and use, is this the same person again?

## 2. What deployments actually ask for

Five anonymized requests show what must persist and what the pseudonym provides:

| Deployment | What they ask for | What must persist | What a scoped pseudonym provides |
| --- | --- | --- | --- |
| Agentic search provider | Free monthly requests per verified human | One monthly allowance across accounts and agents | One allowance record in the service's database |
| Browser-automation platform | Human-backed agent sessions, with bans and shared reputation | A decision that survives a new agent, re-enrollment, or independently issued credential | One reputation and removal record found by later presentations |
| Commerce platform | Limited-edition sales without multiple allocations | Whether this person already received an allocation | One allocation record; a one-use registry also satisfies the stated request |
| Payments/API infrastructure | A free tier before paid access | One allowance across new accounts | One allowance record in the service's database |
| Workflow platform | Human approval before a sensitive agent action | Evidence that a human approved once | Not needed for one approval; useful if later steps require the same person |

In four cases, the pseudonym provides an ordinary service-owned record.

## 3. What is already solved, and by whom

MoLE is the closest alternative. It keeps policy state hidden in a credential. A Moderator (the service or another system) tests that state and may return a replacement credential. MoLE's architecture says, “Two successful presentations cannot be linked to one another.” Clients therefore store and burn one-use credentials and accept replacements when access continues, Moderators prevent double-spending, and some endorsers record issuance. Section 10.2 says that all parties maintain state.

Human Continuity chooses a different boundary. A profile returns a stable scoped pseudonym that the service can use as a database key. Allowance, reputation, and removal records can stay local and change without a credential transition. This is simpler for the service, not necessarily end to end: the underlying verification system still supplies uniqueness and any cross-credential mapping, and defines whether recovery is possible; the service accepts limited linkability.

A one-per-person system also recognizes a repeat, even if only to reject it. PACT states requirements for private human eligibility and rate limits. ACT provides anonymous credits, Privacy Pass supports anonymous authorization, and the discontinued ARC work documented capped anonymous authorization. When these approaches meet the need, they reveal less to the service and are the better answer; the draft says to prefer them.

## 4. What remains

Human Continuity is useful when the service wants to own an evolving per-person record. The service can:

1. Keep allowances, reputation, and removals in its database without defining them in a credential protocol.
2. Find the same record after an account or credential changes, including across accepted issuers when the profile provides a common mapping.
3. Keep a decision in force after re-enrollment or another independently issued credential.
4. Find an existing record after all client-held state is lost, when the profile supports recovery. The pseudonym is not an authenticator.

A hidden-state system can implement some policies with less linkability. If a deployment accepts that credential lifecycle, Human Continuity is not needed. It is warranted only when a service-owned record matters enough to accept the declared, scoped link.

No case proves that a pseudonym is the only design. Search, browser automation, and payments can use one; commerce can use a one-use registry; workflow needs none for one approval. Without a common interface, clients need a custom integration per service rather than one implementation across services. The standards question is whether enough deployments need a service-owned per-person record to justify a common interface and its limited linkability.

## 5. Why this is not a global identifier

The proposal gives no identifier that follows a person across services or purposes. Each pseudonym belongs to one `(realm, attestation audience, purpose)` combination. Under the profile's protections, another combination produces a value that cannot be matched to the first. Other request data or cooperating realm operators may still link people.

A service may reserve a distinct purpose for one HTTP method and path, although neither is part of the pseudonym's scope. Policy metadata declares allowed realms, purposes, profiles, and requests. Before presenting, the client checks fresh or validly cached metadata, or trusted configuration; the service checks the request too. Both refuse uses outside the policy. These checks make the boundary visible to the participating client but cannot narrow a broad purpose.

The authors have found no design that reveals less while giving the service this property, and invite one.

## 6. Carrier

The motivating requests may arrive with no usable account: before signup, when a non-browser agent is checked before association with an account, or during recovery when the person cannot log in. Putting the proof only inside login assumes the missing link. These cases argue for a protocol exchange, but do not by themselves justify HTTP. That question remains open.

## 7. Status

The `-00` Internet-Draft is published and under review.
The issuer- and credential-neutral core defines no profile.
No production profile or client authenticator has been built.
This document seeks review and evidence of shared need, not adoption.
