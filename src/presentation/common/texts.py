class Text:
    @property
    def start(self):
        text = str(
            "Данный бот может выполнять поиск сотрудников и документов.\n"
            + "/news - для получения последних новостей\n"
            + "/info - информация для администратора\n"
            + "/request_access - запросить права администратора"
        )
        return text

    @property
    def info(self):
        text = str(
            "Администратор может обновлять данные по документам и сотрудникам, добавлять других администраторов\n\n"
            + "/announcement - Отправить обьявление всем пользователям\n"
            + "/admins - Список администраторов\n"
            + "/promote_user <id_пользователя> - Выдать права администратора пользователю\n"
            + "/demote_user <id_пользователя> - Забрать права администратора у пользователя\n"
            + "/request_access - Данной командой другие пользователи могут сами запросить права администратора\n"
        )
        return text

    @property
    def permission_denied(self):
        text = str(
            "\U00002757 Недостаточно прав\n\nВы можете запросить права администратора нажав на команду ниже\n\n /request_access"
        )
        return text

    def request_access(self, user_id: int, username: str):
        text = "Пользователь запросил права администратора\n\n*ID:* {0}\n*username:* {1}".format(
            user_id, username
        )
        return text


text = Text()
