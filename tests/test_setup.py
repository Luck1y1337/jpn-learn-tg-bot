import bot_setup
import locales

LANGS = ("ru", "en", "uz")


def test_public_commands_built_for_every_lang():
    for lang in LANGS:
        cmds = bot_setup._commands(bot_setup.PUBLIC_COMMANDS, lang)
        assert len(cmds) == len(bot_setup.PUBLIC_COMMANDS)
        for command in cmds:
            assert command.command
            assert command.description
            # Telegram limits descriptions to 256 chars.
            assert len(command.description) <= 256


def test_admin_commands_include_public_plus_extra():
    admin_defs = bot_setup.PUBLIC_COMMANDS + bot_setup.ADMIN_EXTRA_COMMANDS
    cmds = bot_setup._commands(admin_defs, "ru")
    names = [c.command for c in cmds]
    assert "start" in names          # public entry present
    assert "backup" in names         # admin-only entry present
    assert "restore" in names


def test_commands_fall_back_to_ru_for_unknown_lang():
    cmds = bot_setup._commands(bot_setup.PUBLIC_COMMANDS, "xx")
    ru = bot_setup._commands(bot_setup.PUBLIC_COMMANDS, "ru")
    assert [c.description for c in cmds] == [c.description for c in ru]


def test_menu_and_description_locale_keys_exist():
    keys = ("btn_menu", "hub_header", "bot_description", "bot_short_description")
    for lang in LANGS:
        for key in keys:
            value = locales.get_text(lang, key)
            assert value and value.strip()
    # Short description must respect Telegram's 120-char limit.
    for lang in LANGS:
        assert len(locales.get_text(lang, "bot_short_description")) <= 120
    # Long description must respect Telegram's 512-char limit.
    for lang in LANGS:
        assert len(locales.get_text(lang, "bot_description")) <= 512
