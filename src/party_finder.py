import time
import itertools

# Define a list of distinct hex colors suitable for Rich console
PARTY_COLORS = [
    "#FF5733",  # Orange Red
    "#33FF57",  # Lime Green
    "#3357FF",  # Royal Blue
    "#FF33A1",  # Hot Pink
    "#F1C40F",  # Yellow
    "#8E44AD",  # Purple
    "#1ABC9C",  # Turquoise
    "#E67E22",  # Carrot Orange
    "#2ECC71",  # Emerald Green
    "#3498DB",  # Peter River Blue
    "#E74C3C",  # Alizarin Crimson
    "#9B59B6",  # Amethyst Purple
]


def clear_party_history_cache(requests_obj):
    """Drop transient party-history results so the next refresh refetches them."""
    if hasattr(requests_obj, "_party_history_cache"):
        requests_obj._party_history_cache.clear()

def get_recent_match_history(puuid, Requests_obj, log_func, retries=2, backoff_factor=1):
    """Fetches the last 5 match IDs from the authenticated ranked updates endpoint."""
    endpoint = f"/mmr/v1/players/{puuid}/competitiveupdates?startIndex=0&endIndex=4"
    for attempt in range(retries + 1):
        try:
            response = Requests_obj.fetch('pd', endpoint, 'get', rate_limit_seconds=1)

            if response is None:
                log_func(f"No response fetching match history for {puuid}")
                return set()
            if response.ok:
                matches_data = response.json()
                matches = matches_data.get("Matches", [])
                if not matches:
                    log_func(f"Empty match history found for {puuid} via competitiveupdates")
                    return set()

                match_ids = {
                    match.get("MatchID") for match in matches if match.get("MatchID")
                }
                log_func(f"Fetched {len(match_ids)} match IDs for {puuid} via competitiveupdates")
                return match_ids

            elif response.status_code == 404:
                log_func(f"Match history not found (404) for {puuid} via competitiveupdates")
                return set()
            elif response.status_code == 429:
                wait_time = backoff_factor * (2 ** attempt)
                log_func(f"Rate limited (429) fetching match history for {puuid}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                log_func(f"Error fetching match history for {puuid}: Status {response.status_code}, Response: {response.text}")
                return set()
        except Exception as e:
            log_func(f"Exception fetching match history for {puuid}: {e}")
            if attempt == retries:
                return set()
            wait_time = backoff_factor * (2 ** attempt)
            log_func(f"Retrying fetch for {puuid} in {wait_time}s...")
            time.sleep(wait_time)
    return set()

def find_parties(
    puuids: list[str],
    Requests_obj,
    log_func,
    current_teams: dict[str, str] | None = None,
    authoritative_party_members: set[str] | None = None,
) -> dict[str, tuple[str, str]]:
    """
    Identifies parties based on shared recent match history
    (at least 2 shared matches in the last 5 ranked updates).
    If current_teams is provided (for INGAME state), it also ensures members are on the same current team.
    Returns a dictionary mapping PUUIDs to their assigned party tuple (number_string, color_hex).
    """
    if not puuids:
        return {}

    log_func("Starting party finding...")
    start_time = time.time()

    # Reuse histories between scoreboard refreshes. Team membership is evaluated
    # per call, while the expensive recent-history request is cached briefly.
    now = time.time()
    persistent_cache = getattr(Requests_obj, "_party_history_cache", {})
    Requests_obj._party_history_cache = persistent_cache
    match_history_cache = {}
    party_assignments = {}
    checked_puuids = set()
    # Assign a stable color and number to each detected party.
    next_party_number = 1
    assigned_colors = set()
    color_iterator = itertools.cycle(PARTY_COLORS)

    log_func(f"Fetching recent match history for {len(puuids)} players...")
    for puuid in puuids:
        cache_key = str(puuid).lower()
        cached = persistent_cache.get(cache_key)
        if cached and now - cached[0] < 120:
            match_history_cache[cache_key] = cached[1]
        else:
            match_history_cache[cache_key] = get_recent_match_history(puuid, Requests_obj, log_func)
            persistent_cache[cache_key] = (now, match_history_cache[cache_key])
            time.sleep(0.1)

    log_func("Finished fetching history. Identifying parties...")
    log_func(
        f"Fetched party history for {len(match_history_cache)} players; "
        "omitting match IDs from routine logs"
    )

    # Riot identifiers are case-insensitive. Normalize them before matching
    # history and team membership so opponents are not split into false singles.
    normalized_teams = {
        str(puuid).lower(): team
        for puuid, team in (current_teams or {}).items()
    }
    sorted_puuids = sorted({str(puuid).lower() for puuid in puuids})
    match_history_cache = {
        str(puuid).lower(): history
        for puuid, history in match_history_cache.items()
    }

    # Compare every pair and then group connected matches. This detects
    # opponent parties even when one member has a different recent window.
    graph = {puuid: set() for puuid in sorted_puuids}
    for index, puuid in enumerate(sorted_puuids):
        for other_puuid in sorted_puuids[index + 1:]:
            if current_teams and normalized_teams.get(puuid) != normalized_teams.get(other_puuid):
                continue
            common_matches = match_history_cache.get(puuid, set()).intersection(
                match_history_cache.get(other_puuid, set())
            )
            if len(common_matches) >= 2:
                graph[puuid].add(other_puuid)
                graph[other_puuid].add(puuid)

    for puuid in sorted_puuids:
        if puuid in checked_puuids:
            continue

        current_party = {puuid}
        puuid_history = match_history_cache.get(puuid, set())

        if not puuid_history:
             checked_puuids.add(puuid)
             continue

        for other_puuid in sorted_puuids:
            if other_puuid == puuid or other_puuid in checked_puuids:
                continue

            other_history = match_history_cache.get(other_puuid, set())
            if not other_history:
                continue

            # Require every member of a detected party to share the minimum
            # history threshold with the existing members. This avoids
            # merging two separate parties through one bridge player.
            if other_puuid in graph.get(puuid, set()) and all(
                other_puuid in graph.get(member, set())
                for member in current_party
            ):
                current_party.add(other_puuid)

        if len(current_party) > 1:
            # --- Current Team Check (if applicable) ---
            assign_party = True
            if current_teams:
                party_member_list = list(current_party)
                first_member_team = normalized_teams.get(party_member_list[0])
                if first_member_team is None: # Should not happen if data is consistent
                    log_func(f"Warning: Could not find current team for {party_member_list[0]} in potential party {current_party}")
                    assign_party = False
                else:
                    for member_puuid in party_member_list[1:]:
                        if normalized_teams.get(member_puuid) != first_member_team:
                            log_func(f"Party {current_party} rejected: Members on different current teams.")
                            assign_party = False
                            break # No need to check further members
            # --- End Current Team Check ---

            # A shared history match is not enough to claim that the current
            # authenticated player is presently grouped with someone. Current
            # party membership from the client is authoritative for that case.
            if (
                assign_party
                and authoritative_party_members is not None
                and str(Requests_obj.puuid).lower() in current_party
                and not current_party.issubset(authoritative_party_members)
            ):
                assign_party = False

            if assign_party:
                # Assign the current party number
                party_number_str = str(next_party_number)

                # Assign a unique color
                party_color = next(color_iterator)
                while party_color in assigned_colors:
                    party_color = next(color_iterator)
                    # Basic safety break if all colors somehow get used twice quickly (unlikely)
                    if len(assigned_colors) >= len(PARTY_COLORS) * 2: break
                assigned_colors.add(party_color)

                log_func(f"Found party #{party_number_str} with color {party_color}: {current_party}")

                assignment_value = (party_number_str, party_color)

                for member_puuid in current_party:
                    party_assignments[member_puuid] = assignment_value
                    checked_puuids.add(member_puuid)

                # Increment for the next party
                next_party_number += 1
            # else: Party assignment skipped due to current team mismatch

            # Mark all checked members regardless of assignment outcome for this iteration
            # This prevents individuals from a rejected party forming smaller parties later
            for member_puuid in current_party:
                 checked_puuids.add(member_puuid)

        else: # Single player or failed party checks
             checked_puuids.add(puuid)

    end_time = time.time()
    log_func(f"Party finding finished in {end_time - start_time:.2f} seconds. Assignments: {party_assignments}")
    return party_assignments
