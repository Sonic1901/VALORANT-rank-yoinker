import os
import time
import json


class Stats:
    def __init__(self):
        self.stats_dir = os.path.join(os.getenv("APPDATA"), "vry")
        self.stats_path = os.path.join(self.stats_dir, "stats.json")

    def _ensure_stats_dir(self):
        os.makedirs(self.stats_dir, exist_ok=True)

    @staticmethod
    def _normalise_history(history):
        if isinstance(history, list):
            return [item for item in history if isinstance(item, dict)]
        if isinstance(history, dict):
            return [history]
        return []

    @staticmethod
    def _map_name(map_value):
        if isinstance(map_value, dict):
            return map_value.get("name") or "Unknown"
        return map_value or "Unknown"

    @staticmethod
    def _relation_name(relation):
        if relation == "ally":
            return "teammate"
        if relation == "enemy":
            return "enemy"
        return "player"

    @staticmethod
    def _win_percentage(wins, losses):
        total = wins + losses
        return round((wins / total) * 100) if total else None

    @staticmethod
    def _recent_context(history):
        if not history:
            return {}
        latest = history[0]
        context = {
            "recent_map": Stats._map_name(latest.get("map")),
            "recent_agent": latest.get("agent") or "Unknown",
        }
        try:
            age_seconds = max(0, time.time() - float(latest.get("epoch", 0)))
        except (TypeError, ValueError):
            age_seconds = 0
        if age_seconds <= 12 * 60 * 60:
            context["recent_hours"] = age_seconds / 3600
            context["recent_games_ago"] = 1
        return context

    @classmethod
    def _games_ago(
        cls,
        stats_data,
        encounter_epoch,
        encounter_match_id,
        current_match_id,
        self_puuid,
    ):
        if self_puuid is None:
            return None
        try:
            encounter_time = float(encounter_epoch)
        except (TypeError, ValueError):
            return None

        newer_match_ids = set()
        for entry in cls._history_for(stats_data, self_puuid):
            match_id = entry.get("match_id")
            if (
                not match_id
                or match_id == current_match_id
                or match_id == encounter_match_id
            ):
                continue
            try:
                entry_time = float(entry.get("epoch"))
            except (TypeError, ValueError):
                continue
            if entry_time > encounter_time:
                newer_match_ids.add(match_id)
        return len(newer_match_ids) + 1

    @classmethod
    def _history_for(cls, stats_data, puuid):
        history = stats_data.get(puuid)
        if history is not None:
            return cls._normalise_history(history)
        wanted = str(puuid).lower()
        for subject, entries in stats_data.items():
            if str(subject).lower() == wanted:
                return cls._normalise_history(entries)
        return []

    def _write_data(self, data):
        self._ensure_stats_dir()
        temp_path = f"{self.stats_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, self.stats_path)

    def save_data(self, data):
        original_data = self.read_data()
        updated_data = {
            puuid: self._normalise_history(history)
            for puuid, history in original_data.items()
        }

        for puuid, entry in data.items():
            if not isinstance(entry, dict):
                continue

            history = updated_data.setdefault(puuid, [])
            match_id = entry.get("match_id")
            if match_id:
                for index, existing_entry in enumerate(history):
                    if existing_entry.get("match_id") == match_id:
                        merged_entry = existing_entry.copy()
                        for key, value in entry.items():
                            if (
                                key in ("result", "score", "winning_team")
                                and value is None
                                and merged_entry.get(key) is not None
                            ):
                                continue
                            merged_entry[key] = value
                        history[index] = merged_entry
                        break
                else:
                    history.append(entry)
            else:
                history.append(entry)

        self._write_data(updated_data)

    def read_data(self):
        try:
            with open(self.stats_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def build_encounter_summary(
        self,
        stats_data,
        puuid,
        current_match_id,
        fallback_name="#",
        fallback_relation=None,
        self_puuid=None,
    ):
        history = self._history_for(stats_data, puuid)
        if not history:
            return None

        previous_entries = []
        seen_match_ids = set()
        for entry in reversed(history):
            match_id = entry.get("match_id")
            if match_id == current_match_id:
                continue
            dedupe_key = match_id or id(entry)
            if dedupe_key in seen_match_ids:
                continue
            seen_match_ids.add(dedupe_key)
            previous_entries.append(entry)

        if not previous_entries:
            return None

        latest = previous_entries[0]
        ally_wins = ally_losses = ally_unknown = 0
        enemy_wins = enemy_losses = enemy_unknown = 0
        for entry in previous_entries:
            result = entry.get("result")
            # Older stats files predate explicit relation fields. Use the
            # current encounter relation for those entries instead of
            # silently reporting zero records.
            rel = entry.get("relation") or fallback_relation
            if rel in ("ally", "premade"):
                if result == "win":
                    ally_wins += 1
                elif result == "loss":
                    ally_losses += 1
                else:
                    ally_unknown += 1
            elif rel == "enemy":
                if result == "win":
                    enemy_wins += 1
                elif result == "loss":
                    enemy_losses += 1
                else:
                    enemy_unknown += 1

        latest_epoch = latest.get("epoch", time.time())
        try:
            time_diff = time.time() - float(latest_epoch)
        except (TypeError, ValueError):
            time_diff = 0

        latest_relation = latest.get("relation") or fallback_relation
        latest_name = latest.get("name")
        if not latest_name or latest_name == "#":
            latest_name = fallback_name
        historical_names = [
            entry.get("name")
            for entry in previous_entries
            if entry.get("name") and entry.get("name") != "#"
        ]
        previous_name = next(
            (
                historical_name
                for historical_name in reversed(historical_names)
                if historical_name != fallback_name
            ),
            None,
        )
        return {
            "times": len(previous_entries),
            "name": latest_name,
            "agent": latest.get("agent") or "Unknown",
            "map": self._map_name(latest.get("map")),
            "relation": latest_relation,
            "relation_name": self._relation_name(latest_relation),
            "time_diff": max(0, time_diff),
            "ally_wins": ally_wins,
            "ally_losses": ally_losses,
            "ally_unknown": ally_unknown,
            "ally_count": ally_wins + ally_losses + ally_unknown,
            "enemy_wins": enemy_wins,
            "enemy_losses": enemy_losses,
            "enemy_unknown": enemy_unknown,
            "enemy_count": enemy_wins + enemy_losses + enemy_unknown,
            **self._recent_context(previous_entries),
            "previous_name": previous_name,
            "recent_games_ago": self._games_ago(
                stats_data,
                latest.get("epoch"),
                latest.get("match_id"),
                current_match_id,
                self_puuid,
            ),
        }

    def build_personal_summary(self, stats_data, puuid, name="#"):
        history = self._history_for(stats_data, puuid)
        wins = sum(1 for entry in history if entry.get("result") == "win")
        losses = sum(1 for entry in history if entry.get("result") == "loss")
        return {
            "name": name,
            "wins": wins,
            "losses": losses,
            "count": wins + losses,
            "win_percentage": self._win_percentage(wins, losses),
        }

    def build_premade_summary(
        self,
        stats_data,
        puuid,
        current_match_id,
        name="#",
        self_puuid=None,
    ):
        history = []
        seen_match_ids = set()
        for entry in reversed(self._history_for(stats_data, puuid)):
            match_id = entry.get("match_id")
            if match_id == current_match_id:
                continue
            if match_id and match_id in seen_match_ids:
                continue
            if match_id:
                seen_match_ids.add(match_id)
            history.append(entry)
        overall_wins = sum(1 for entry in history if entry.get("result") == "win")
        overall_losses = sum(1 for entry in history if entry.get("result") == "loss")
        explicit_queued = {
            entry.get("match_id")
            for entry in history
            if (
                entry.get("relation") == "premade"
                or str(entry.get("premade", "")).strip().lower()
                in {"true", "1", "yes"}
            )
        }
        # Older stats.json files predate the premade/relation fields. For a
        # teammate currently confirmed as premade, shared completed match IDs
        # with the player's own history provide a safe migration fallback.
        own_match_ids = set()
        if self_puuid:
            own_match_ids = {
                entry.get("match_id")
                for entry in self._history_for(stats_data, self_puuid)
                if entry.get("match_id") and entry.get("match_id") != current_match_id
            }
        queued = [
            entry for entry in history
            if entry.get("match_id") in explicit_queued
            or (
                entry.get("match_id") in own_match_ids
                and not entry.get("relation")
            )
        ]
        queued_wins = sum(1 for entry in queued if entry.get("result") == "win")
        queued_losses = sum(1 for entry in queued if entry.get("result") == "loss")
        if not history:
            return None
        return {
            "name": name,
            "overall_wins": overall_wins,
            "overall_losses": overall_losses,
            # Unknown legacy entries must not inflate a completed W/L total.
            "overall_count": overall_wins + overall_losses,
            "queued_wins": queued_wins,
            "queued_losses": queued_losses,
            "queued_count": queued_wins + queued_losses,
            "overall_win_percentage": self._win_percentage(
                overall_wins, overall_losses
            ),
            "queued_win_percentage": self._win_percentage(
                queued_wins, queued_losses
            ),
        }

    def format_encounter_summary(self, played):
        ally_count = played.get("ally_count", 0)
        enemy_count = played.get("enemy_count", 0)

        if ally_count and enemy_count:
            encounter_label = "played with/against"
        elif enemy_count:
            encounter_label = "encountered"
        else:
            encounter_label = "played with"
        parts = [
            f"Already {encounter_label} {played['name']} "
            f"({played['times']} times"
        ]
        if ally_count:
            parts.append(f" — {ally_count} as ally")
        if enemy_count:
            parts.append(f", {enemy_count} as enemy")
        parts.append("). ")

        parts.append(
            f"Last seen: {played['relation_name']} {played['agent']} "
            f"on {played['map']} {self.convert_time(played['time_diff'])} ago."
        )

        if ally_count:
            ally_record = f"{played['ally_wins']}W-{played['ally_losses']}L"
            if played["ally_unknown"]:
                ally_record += f" ({played['ally_unknown']} unknown)"
            parts.append(f" With: {ally_record}.")
        if enemy_count:
            enemy_record = f"{played['enemy_wins']}W-{played['enemy_losses']}L"
            if played["enemy_unknown"]:
                enemy_record += f" ({played['enemy_unknown']} unknown)"
            parts.append(f" Against: {enemy_record}.")

        return "".join(parts)

    def update_match_result(self, match_id, my_team, winning_team, score=None):
        if not match_id or not my_team or not winning_team:
            return False

        stats_data = self.read_data()
        changed = False
        my_result = "win" if my_team == winning_team else "loss"
        for puuid, history in list(stats_data.items()):
            normalised_history = self._normalise_history(history)
            if normalised_history is not history:
                stats_data[puuid] = normalised_history

            for entry in normalised_history:
                if entry.get("match_id") != match_id:
                    continue

                # Results are always stored from the tracked player's
                # perspective. The encounter UI's "Against" line describes
                # our record against that opponent, not the opponent's own
                # win/loss record.
                result = my_result
                updates = {
                    "result": result,
                    "winning_team": winning_team,
                    "score": score,
                }
                for key, value in updates.items():
                    if entry.get(key) != value:
                        entry[key] = value
                        changed = True

        if changed:
            self._write_data(stats_data)
        return changed

    @staticmethod
    def convert_time(s):
        s = int(s)
        if s < 60:
            return f"{s} second" if s == 1 else f"{s} seconds"
        if s < 3600:
            return f"{s // 60} minute" if s // 60 == 1 else f"{s // 60} minutes"
        if s < 86400:
            return f"{s // 3600} hours" if s // 3600 == 1 else f"{s // 3600} hours"
        return f"{s // 86400} days" if s // 86400 == 1 else f"{s // 86400} days"
