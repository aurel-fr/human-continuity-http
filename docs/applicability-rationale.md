# Design rationale: scoped human continuity vs unlinkable mechanisms

This is informative background for the "Applicability and Alternatives" section of
`draft-brezun-human-continuity-http`. It explains why a scoped, verifier-local human
continuity handle is the minimal primitive for mutable per-human allocation, when an
unlinkable mechanism or operator-mediated allocation is the better choice instead, and
what abuse the primitive does and does not prevent. It is not part of the protocol
contract; if it disagrees with the draft's normative prose, the prose prevails.

## Capability systems vs policy-state systems

The boundary between this work and unlinkable mechanisms turns on _when_ each binds
policy.

A **capability system** fixes a spendable allowance and its anonymity envelope at
issuance time. Every decision-time check reads state attached to the _artifact_ — a
still-valid token, a not-yet-exhausted credential, an unspent credit — never state
attached to the _human_. Privacy Pass ([RFC 9576](https://www.rfc-editor.org/rfc/rfc9576.html)),
the Privacy Pass HTTP authentication scheme ([RFC 9577](https://www.rfc-editor.org/rfc/rfc9577.html)),
ARC ([draft-ietf-privacypass-arc-crypto](https://datatracker.ietf.org/doc/draft-ietf-privacypass-arc-crypto/)),
and ACT ([draft-schlesinger-cfrg-act](https://datatracker.ietf.org/doc/draft-schlesinger-cfrg-act/))
are capability systems: a Privacy Pass origin prevents a token with the same nonce from
being redeemed twice, ACT detects reuse through nullifiers, and ARC checks a
per-presentation tag for prior use. None of these decisions reach mutable, per-human
state across an open-ended event history.

A **policy-state system** binds policy at decision time. The verifier reads mutable
per-human state — a per-human row it maintains verifier-locally within a continuity
scope — to determine whether a request belongs to the same human as previous requests.

The distinction is the subject of the decision. A capability system asks "is this bearer
presenting a still-valid capability?" A policy-state system asks "does this request
belong to the same human across an open-ended event history?"

## Why unlinkability is structurally insufficient for mutable per-human allocation

Unlinkability becomes structurally insufficient precisely when policy must contract,
after artifacts are already in circulation, in a way that turns on distinguishing
humans.

Consider two valid redemptions arriving at one verifier. In scenario A, Alice redeems two
valid artifacts; in scenario B, Alice redeems one and Bob redeems one. Under unlinkability
the verifier cannot distinguish scenario A from scenario B from the redemption transcript. A
policy that contracts to "one per human" demands different outcomes between them:
rejecting or clawing back a redemption in scenario A while accepting both in scenario B. A
verifier cannot be simultaneously unable to distinguish the two scenarios and able to
enforce a rule whose result turns on that distinction.

Therefore, as long as already-issued artifacts remain unlinkable, post-issuance
per-human policy contraction is not expressible from the transcript. The available exits
are narrow:

1. invalidate and reissue every holder;
2. trust the client to self-enforce;
3. move per-human policy state to the realm operator; or
4. reveal a verifier-local continuity value.

The last exit is the primitive the draft defines.

## Alternatives and their costs

### Fixed caps known in advance: prefer ARC

When the desired cap is fixed in advance and can be enforced per credential or per
issued artifact rather than per human, the contraction above never arises and a
fixed-limit capability suffices without any per-human record. The cap ARC enforces is
_per credential_, so it fits only when a fixed per-credential presentation
limit is the actual requirement. ARC enforces such a cap cryptographically: client and
server agree on a fixed presentation limit, presentations do not verify if the limits
differ, presentations stay pairwise unlinkable up to that limit, and the server stores
only the per-presentation tag for double-spend detection rather than a per-human row.

### Operator-mediated allocation

Moving the per-human rule to the realm operator is the remaining transcript-preserving exit. A
realm operator or allocation service enforces the per-human rule itself and returns only an
eligibility result or a single spendable capability, so the origin never sees a
continuity value. The cost is centralization: the origin loses local policy mutation,
local auditability, local fraud investigation, and local reconciliation, and the realm operator
becomes the allocation authority for the rule. A scoped continuity handle keeps that
authority at the origin.

## What a scoped handle does and does not prevent

For allocation and abuse-control use cases, a scoped continuity handle does not eliminate
abuse; it changes the attacker's bottleneck from creating accounts to obtaining access to
distinct verified humans. Paid human farms, collusion,
and resale of access remain possible against any one-per-human rule.
