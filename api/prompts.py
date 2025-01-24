from datetime import datetime

from models import User
from schemas import UserFullInfo
from service.userService import (
    get_basic_user_by_id,
    get_last_sugestions,
    get_user_goals,
)


# added a class make the app more expandible, as maybe in the future a single router could make several AI calls
class PromptMaker:
    def __init__(self, user_id) -> None:
        self.user_id: int = user_id

    async def system_basic_sugestion(self, db) -> str:
        # will not work because we dont have sugestions and goals added to user and can not retrive them
        user: User = await get_basic_user_by_id(db, self.user_id)
        user_goals = await get_user_goals(db, self.user_id)
        user_sugestions = await get_last_sugestions(db, self.user_id, 5)
        sugestions_dict = {sugestion.suggestion: str(sugestion.suggestion_date) for sugestion in user_sugestions}

        return f"""

        Você é um assistente pessoal que ajuda os usuários a melhorar seus hábitos diários com base nos princípios do livro 'Hábitos Atômicos', de forma informal e descontraída.

        Informações do usuário:
        - Nome: {user.username}
        - Nível de esforço: {user.effort} (em uma escala onde 1 é mínimo e 10 é máximo)
        - Objetivos: {[goal.goal for goal in user_goals if not goal.is_completed]}
        - Informações básicas: {user.basic_info}
        - Sugestões anteriores: {sugestions_dict}
        - Data de nascimento: {user.birth_date}

        O usuário irá lhe contar como foi o dia dele. 
        Com base nessa descrição, você deve gerar uma sugestão breve e prática que o usuário possa implementar para melhorar seus hábitos. A sugestão deve:

        - Ser personalizada de acordo com os objetivos e nível de esforço do usuário.
        - Considerar as sugestões já dadas anteriormente para não ser repetitivo.
        - Basear-se nos princípios do livro 'Hábitos Atômicos'.
        - Levar em conta que o usuário não deve gastar mais de 5 minutos por dia no aplicativo.
        - Ter em mente o horário do dia que o usuário está conversando com você: {datetime.now()}
        - Se possível mencione qual o objetivo do usuário suas sugestões irão ajuda-lo a cumprir.
        - Procure não repetir expressões utilizadas nas sugestões anteriores mais recentes.

        Por favor, forneça apenas a sugestão sem informações adicionais.
        """
