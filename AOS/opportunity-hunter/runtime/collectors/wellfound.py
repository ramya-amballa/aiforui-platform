"""
Wellfound (formerly AngelList Talent) connector — connector-ready,
awaiting API access.

Wellfound does not currently publish a public, self-serve API or RSS
feed for job search — its earlier AngelList Talent developer API was
discontinued. No compliant public or partner access path is documented
today, so this connector deliberately does not scrape Wellfound's
listings pages. If Wellfound introduces an official API or partner
integration in the future, this module's collect(keywords, config)
signature already matches every working connector, so wiring it in is
a config change plus one implementation, not a rewrite — normalise
each result with collectors.common.build_opportunity(...), exactly
like greenhouse.py.

See ../../CONNECTOR-CONFIGURATION-GUIDE.md for how to re-check whether
an access path has since become available.
"""

SOURCE_NAME = "Wellfound"


def collect(keywords, config):
    if not config.get("apiKey"):
        print(f"  {SOURCE_NAME}: connector-ready, no known public/partner API to "
              f"authenticate against yet — skipping")
        return []
    # Not implemented: no documented API contract exists to code against
    # yet. If an apiKey has been set, an access path has presumably been
    # identified since this was written — implement the real call here.
    print(f"  {SOURCE_NAME}: API key present but the API call is not yet implemented "
          f"— see the module docstring")
    return []
