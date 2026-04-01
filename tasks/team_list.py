

# Весь этот код взят с репозитория моего братка - https://github.com/Schrodinger71/Dev-bot/blob/c525f3a847a7e3c314ff93409cfd2f9591292a6a/tasks/list_team_task.py#L187


from disnake import Embed
from disnake.ext import commands, tasks
from disnake.utils import get

from dataConfig import ROLE_ACCESS_TOP_HEADS

from bot_init import bot
from disnake.ext.commands import has_any_role

roles_team = [
    # Список ролей и их ID
    # Руководство проекта
    ("Хост", 1474158623834898653),
    ("Руководство проекта", 1474158624166383748),

    # Администрация
    ("Куратор модерации", 1474158624136757523),
    ("Ведущий модератор", 1474158624107532423),
    ("Старший модератор", 1474158624053137437),
    ("Модератор", 1474158624053137428),
    ("Младший Модератор", 1474158623981568252),

    # Дискорд модерация
    ("Куратор караула", 1474158624136757521),
    ("Старший караульный", 1474158624053137435),
    ("Караульный", 1474158623981568259),
    ("Младший караульный", 1474158623935692859),

    # Ивентология
    ("Куратор ивентологии", 1474158624136757522),
    ("Ведущий ивентолог", 1474158624107532422),
    ("Старший ивентолог", 1474158624053137436),
    ("Ивентолог", 1474158623981568260),
    ("Младший ивентолог", 1474158623981568251),

    # Маппинг отдел
    ("Бригадир мапперов", 1474158624107532426),
    ("Старший маппер", 1474158624053137431),
    ("Маппер", 1474158623981568255),
    ("Маппер стажёр", 1488927899032621136),

    # Вики отдел
    ("Куратор вики", 1474158624107532428),
    ("Куратор лороведов", 1474158624107532427),
    ("Викивод", 1474158623981568257),
    ("Младший викивод", 1474158623935692857),
    ("Младший лоровед", 1474158623935692856),

    # Спрайт отдел
    ("Куратора спрайтеров", 1474158624107532429),
    ("Старший спрайтер", 1474158624053137434),
    ("Спрайтер", 1474158623981568258),
    ("Младший спрайтер", 1474158623935692858),

    # Отдел Разработки
    ("Глава разработчик", 1474158624136757530),
    ("Старший тех. мастер", 1474158624107532420),
    ("Тех. мастер", 1474158624053137429),
    ("Младший тех. мастер", 1474158623981568253),

    # Ютуберы
    ("Медиа", 1488928560122040502),
]

# Определяем цвет для каждой категории
color_map = {
    "Руководство": 0xFFFFFF,  # Белый
    "Отдел Модерации": 0xFF0000,  # Красный
    "Департамент обжалования": 0xFF0000,  # Красный
    "Дискорд Модерация": 0xAAFFCF,  # Ярко-зеленый салатовый
    "Спец роли администрации": 0xFF0000,  # Красный
    "Отдел Ивентологии": 0x50cfc4, # Бирюзовый
    "Отдел Маппинга": 0xFFA500,  # Оранжевый
    "Отдел Вики": 0x0000FF,  # Синий
    "Отдел Спрайтинга": 0xFFC0CB,  # Розовый
    "Отдел Квентологии": 0xA52A2A,  # Коричневый
    "Отдел Разработки": 0x00FF00,  # Зеленый
    "Отдел Медиа": 0xFF0000,  # Красный
}

# Группируем роли по категориям
roles_by_category = {
    "Руководство": [
        ("Хост", 1474158623834898653),
        ("Руководство проекта", 1474158624166383748),
    ],
    "Отдел Модерации": [
        ("Куратор модерации", 1474158624136757523),
        ("Ведущий модератор", 1474158624107532423),
        ("Старший модератор", 1474158624053137437),
        ("Модератор", 1474158624053137428),
        ("Младший Модератор", 1474158623981568252),
    ],
    "Караул": [
        ("Куратор караула", 1474158624136757521),
        ("Старший караульный", 1474158624053137435),
        ("Караульный", 1474158623981568259),
        ("Младший караульный", 1474158623935692859),
    ],
    "Отдел Ивентологии": [
        ("Куратор ивентологии", 1474158624136757522),
        ("Ведущий ивентолог", 1474158624107532422),
        ("Старший ивентолог", 1474158624053137436),
        ("Ивентолог", 1474158623981568260),
        ("Младший ивентолог", 1474158623981568251),
    ],
    "Отдел Маппинга": [
        ("Бригадир мапперов", 1474158624107532426),
        ("Старший маппер", 1474158624053137431),
        ("Маппер", 1474158623981568255),
        ("Маппер стажёр", 1488927899032621136),
    ],
    "Отдел Вики": [
        ("Куратор вики", 1474158624107532428),
        ("Куратор лороведов", 1474158624107532427),
        ("Викивод", 1474158623981568257),
        ("Младший викивод", 1474158623935692857),
        ("Младший лоровед", 1474158623935692856),
    ],
    "Отдел Спрайтинга": [
        ("Куратора спрайтеров", 1474158624107532429),
        ("Старший спрайтер", 1474158624053137434),
        ("Спрайтер", 1474158623981568258),
        ("Младший спрайтер", 1474158623935692858),
    ],
    "Отдел Разработки": [
        ("Глава разработчик", 1474158624136757530),
        ("Старший тех. мастер", 1474158624107532420),
        ("Тех. мастер", 1474158624053137429),
        ("Младший тех. мастер", 1474158623981568253),
    ],
    "Отдел Медиа": [("Медиа", 1488928560122040502)],
}

@bot.command(name="list_team")
@has_any_role(*ROLE_ACCESS_TOP_HEADS)
async def list_team(ctx):
    """
    Команда для отображения состава команды по категориям.
    """
    await ctx.channel.purge(limit=15)

    # Обработка каждой категории
    for category, roles_team in roles_by_category.items(): # pylint: disable=W0621
        color = color_map.get(category, 0xFFFFFF)  # Выбор цвета
        embed = Embed(
            title=category,
            color=color,
            description=f"**👑 Состав команды в категории: {category}**",
        )

        # Добавляем иконку или изображение для каждой категории
        embed.set_thumbnail(
            url="https://example.com/your_icon.png"
        )  # Замените на свой URL изображения

        # Заголовок с эмодзи и стилями
        embed.add_field(
            name=f"**🌟 {category} Роли**",
            value="Все участники в данной категории:",
            inline=False,
        )

        for role_name, role_id in roles_team:
            role = get(ctx.guild.roles, id=role_id)
            if role:
                # Получаем URL иконки роли (если она есть)
                role_icon_url = role.icon.url if role.icon else None

                members = [f"<@{member.id}>" for member in role.members]
                members_count = len(members)

                if members_count > 1:
                    field_value = ", ".join(members)
                    embed.add_field(
                        name=f"**{role_name}** ({members_count})",
                        value=field_value,
                        inline=False,
                    )
                elif members_count == 1:
                    field_value = members[0]
                    embed.add_field(
                        name=f"**{role_name}**",
                        value=f"{field_value}",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"**❌ {role_name}**",
                        value="Нет участников",
                        inline=False,
                    )

                # Если есть значок роли, добавляем его как изображение
                if role_icon_url:
                    embed.set_thumbnail(url=role_icon_url)

            else:
                embed.add_field(
                    name=f"**❌ {role_name}**",
                    value="Роль не найдена",
                    inline=False,
                )

        await ctx.send(embed=embed)


@list_team.error
async def list_team_error(ctx, error):
    """
    Обработчик ошибок для команды list_team.

    Аргументы:
    ctx - контекст команды
    error - объект ошибки
    """
    if isinstance(error, commands.CheckFailure):
        await ctx.send("🚫 У вас нет прав на использование этой команды.")
    else:
        await ctx.send(f"❗ Произошла ошибка: {error}")


@tasks.loop(hours=12)
async def list_team_task(): # pylint: disable=R0912
    """
    Задача, выполняющаяся каждые 12 часов. Очищает канал от последних 15 сообщений.
    Ожидается, что ID канала уже известен. Выводит полный список команды.
    """
    channel = bot.get_channel(1297158288063987752)  # ID канала
    if channel:
        await channel.purge(limit=15)

        for category, roles_team in roles_by_category.items(): # pylint: disable=W0621
            color = color_map.get(category, 0xFFFFFF)  # Выбор цвета
            embed = Embed(
                title=category,
                color=color,
                description=f"**👑 Состав команды в категории: {category}**",
            )

            embed.set_thumbnail(
                url="https://example.com/your_icon.png"
            )  # Замените на свой URL изображения

            # Добавляем поле для заголовка
            embed.add_field(
                name=f"**🌟 {category} Роли**",
                value="Все участники в данной категории:",
                inline=False,
            )

            for role_name, role_id in roles_team:
                role = get(channel.guild.roles, id=role_id)
                if role:
                    role_icon_url = role.icon.url if role.icon else None
                    members = [f"<@{member.id}>" for member in role.members]
                    members_count = len(members)

                    if members_count > 1:
                        embed.add_field(
                            name=f"**{role_name}** ({members_count})",
                            value=", ".join(members),
                            inline=False,
                        )
                    elif members_count == 1:
                        embed.add_field(
                            name=f"**{role_name}**",
                            value=f"{members[0]}",
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=f"**❌ {role_name}**",
                            value="Нет участников",
                            inline=False,
                        )

                    # Если у роли есть иконка, добавляем её
                    if role_icon_url:
                        embed.set_thumbnail(url=role_icon_url)

                else:
                    embed.add_field(
                        name=f"**❌ {role_name}**",
                        value="Роль не найдена",
                        inline=False,
                    )

            # Добавление иконки для Вики Отдела
            if category == "Отдел Вики":
                viki_editor_role = get(channel.guild.roles, id=1084840686303580191)
                if viki_editor_role and viki_editor_role.icon:
                    embed.set_thumbnail(url=viki_editor_role.icon.url)

            if category == "Отдел Маппинга":
                mapper_role = get(channel.guild.roles, id=1062660322386784307)
                if mapper_role and mapper_role.icon:
                    embed.set_thumbnail(url=mapper_role.icon.url)

            if category == "Отдел Администрации":
                admin_role = get(channel.guild.roles, id=1248665281748795392)
                if admin_role and admin_role.icon:
                    embed.set_thumbnail(url=admin_role.icon.url)

            if category == "Отдел Ивентологии":
                admin_role = get(channel.guild.roles, id=1395295618879979621)
                if admin_role and admin_role.icon:
                    embed.set_thumbnail(url=admin_role.icon.url)

            await channel.send(embed=embed)