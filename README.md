<!-- regenerate: off (set to on to let the template rewrite this file) -->

# Human Continuity for HTTP

This is the working area for the individual Internet-Draft, "Human Continuity for HTTP".

- [Editor's Copy](https://aurel-fr.github.io/human-continuity-http/#go.draft-brezun-human-continuity-http.html)
- [Datatracker Page](https://datatracker.ietf.org/doc/draft-brezun-human-continuity-http)
- [Individual Draft](https://datatracker.ietf.org/doc/html/draft-brezun-human-continuity-http)
- [Compare Editor's Copy to Individual Draft](https://aurel-fr.github.io/human-continuity-http/#go.draft-brezun-human-continuity-http.diff)

## Supporting Material

The following are informative and are not part of the protocol contract. Where
they disagree with the draft's normative prose, the prose prevails.

- [`docs/problem-statement.md`](docs/problem-statement.md) describes the need to
  recognize the same person again, what a scoped verifier-local pseudonym
  provides, and when an unlinkable mechanism is preferable.
- [`schemas/`](schemas/) holds JSON Schemas for the policy metadata and realm
  metadata documents. Every metadata example in the draft is validated against
  them in CI:

```sh
$ python3 -m pip install 'jsonschema[format]==4.26.0'
$ python3 scripts/validate-metadata-examples.py
```

## Contributing

See the
[guidelines for contributions](https://github.com/aurel-fr/human-continuity-http/blob/main/CONTRIBUTING.md).

The contributing file also has tips on how to make contributions, if you
don't already know how to do that.

## Command Line Usage

Formatted text and HTML versions of the draft can be built using `make`.

```sh
$ make
```

Command line usage requires that you have the necessary software installed. See
[the instructions](https://github.com/martinthomson/i-d-template/blob/main/doc/SETUP.md).
