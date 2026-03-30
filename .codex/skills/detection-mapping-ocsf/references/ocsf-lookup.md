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

- Prefer exact OCSF paths such as `time`, `src_endpoint.ip`, `dst_endpoint.port`, `http_request.user_agent`, or `network_connection_info.protocol_name` when they fit the rule field semantics directly.
- Reuse an existing OCSF path already present in nearby mappings when the meaning matches.
- Translate OCSF semantics into repo `canonical.*` names only when the repo intentionally uses an internal abstraction or when no clean direct OCSF path exists.
- Reuse repo-specific canonical names already present in existing dictionaries only when that internal contract is still the better fit, for example:
  `canonical.event.action`
  `canonical.http_request.x_header`
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

Then keep those direct OCSF paths unless the existing mapping file has a justified repo-specific `canonical.*` contract that fits better.
