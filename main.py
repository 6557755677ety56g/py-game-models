import json

from django.db import transaction

import init_django_orm  # noqa: F401
from db.models import Guild, Player, Race, Skill


def main() -> None:
    with open("players.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    players_data = data.values() if isinstance(data, dict) else data

    for player in players_data:
        if not isinstance(player, dict):
            continue

        nickname = player.get("nickname")
        race_data = player.get("race", {})
        race_name = (
            race_data.get("name") if isinstance(race_data, dict) else None
        )

        if not nickname or not race_name:
            continue

        with transaction.atomic():
            race, _ = Race.objects.get_or_create(
                name=race_name,
                defaults={"description": race_data.get("description", "")},
            )

            guild = None
            guild_data = player.get("guild")
            if isinstance(guild_data, dict) and guild_data.get("name"):
                guild, _ = Guild.objects.get_or_create(
                    name=guild_data["name"],
                    defaults={
                        "description": guild_data.get("description", "")
                    },
                )

            skills_data = (
                player.get("skills") or player.get("skill") or []
            )
            if isinstance(skills_data, dict):
                skills_data = [skills_data]

            player_skills = []
            for skill_data in skills_data:
                if (
                    not isinstance(skill_data, dict)
                    or not skill_data.get("name")
                ):
                    continue

                skill, _ = Skill.objects.get_or_create(
                    name=skill_data["name"],
                    race=race,
                    defaults={"bonus": skill_data.get("bonus", "")},
                )
                player_skills.append(skill)

            player_obj, _ = Player.objects.get_or_create(
                nickname=nickname,
                defaults={
                    "email": player.get("email", ""),
                    "bio": player.get("bio", ""),
                    "race": race,
                    "guild": guild,
                },
            )

            if player_skills:
                player_obj.skills.add(*player_skills)


if __name__ == "__main__":
    main()
