# OCSF Lookup

## Preferred Local Reference

- Use `.tmp/ocsf-schema/` as the primary local OCSF source.
- Start from `events/<domain>/<event>.json`.
- Then open the object files named by the event attributes, for example `objects/http_request.json` or `objects/url.json`.

## Fast Lookup Paths

- Web access or WAF semantics:
  `events/application/web_resources_activity.json`
  `objects/http_request.json`
  `objects/url.json`
  `objects/web_resource.json`
- HTTP transport semantics:
  `events/network/http_activity.json`
  `objects/http_request.json`
  `objects/http_response.json`
- Generic endpoint semantics:
  `objects/network_endpoint.json`
  `objects/endpoint.json`

## Repo-Specific Translation Rules

- Translate OCSF semantics into repo `canonical.*` names when the repo already uses that pattern.
- Reuse the canonical names already present in existing dictionaries, for example:
  `canonical.event.time`
  `canonical.source.ip`
  `canonical.destination.port`
  `canonical.network.protocol`
- Keep detection-driven additions narrow: map only the user-defined required rule fields and their obvious aliases.

## Practical Example

For a web access rule that requires:

- `http_user_agent`
- `http_referrer`
- `uri_path`
- `uri_query`
- `URL`
- `src_ip`

Use OCSF semantics like:

- `http_request.user_agent`
- `http_request.referrer`
- `http_request.url.path`
- `http_request.url.query_string`
- `http_request.url.url_string`
- `src_endpoint.ip`

Then translate to repo canonical fields by first checking whether the existing mapping file already uses those exact paths or an established `canonical.*` form.
