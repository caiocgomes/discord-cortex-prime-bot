"""Help command with contextual topic variants."""

import logging

from discord import app_commands, Interaction
from discord.ext import commands

log = logging.getLogger(__name__)

HELP_GERAL = (
    "Cortex Bot: gerenciador de sessao para Cortex Prime.\n"
    "\n"
    "Fluxo basico: /campaign setup para criar campanha, "
    "/scene start para iniciar cena, /roll para rolar dados.\n"
    "\n"
    "Grupos de comandos:\n"
    "- /campaign: criar, encerrar, ver info da campanha, delegar\n"
    "- /scene: iniciar, encerrar, ver info da cena\n"
    "- /roll: rolar dados com assets e extras\n"
    "- /gmroll: rolagem do GM/NPC sem estado pessoal\n"
    "- /asset: adicionar, step up, step down, remover assets\n"
    "- /stress: adicionar, step up, step down, remover stress\n"
    "- /complication: adicionar, step up, step down, remover complications\n"
    "- /pp: adicionar e gastar plot points\n"
    "- /xp: adicionar e remover experience points\n"
    "- /doom: doom pool (se habilitado)\n"
    "- /crisis: crisis pools (se habilitado)\n"
    "- /hero: hero dice (se habilitado)\n"
    "- /trauma: trauma (se habilitado)\n"
    "- /undo: desfazer ultima acao\n"
    "\n"
    "Use /help topic:gm para comandos de GM, "
    "/help topic:jogador para comandos de jogador, "
    "/help topic:rolagem para referencia de dados."
)

HELP_GM = (
    "Comandos de GM, organizados por momento.\n"
    "\n"
    "Setup da campanha:\n"
    "- /campaign setup name:\"Nome\" players:@Alice @Bob stress_types:\"Physical,Mental\"\n"
    "  Cria campanha no canal. Voce se torna GM automaticamente.\n"
    "- /campaign delegate player:@Alice - promover jogador a delegado\n"
    "- /campaign undelegate player:@Alice - revogar delegacao\n"
    "\n"
    "Durante a cena:\n"
    "- /stress add player:@Alice type:Physical die:d8 - adicionar stress\n"
    "- /stress stepup player:@Alice type:Physical - step up de stress\n"
    "- /complication add name:\"On Fire\" die:d6 player:@Alice - criar complication\n"
    "- /asset add name:\"Cover\" die:d8 scene_asset:True - criar asset de cena\n"
    "- /doom add die:d6 - adicionar dado ao doom pool\n"
    "- /doom roll - rolar o doom pool\n"
    "- /gmroll dice:2d8 1d10 - rolar como GM/NPC\n"
    "\n"
    "Entre cenas:\n"
    "- /scene start name:\"Tavern Fight\" - iniciar nova cena\n"
    "- /scene end - encerrar cena (remove assets e complications de cena)\n"
    "- /scene end bridge:True - bridge scene: step down de todo stress\n"
    "\n"
    "Administracao:\n"
    "- /campaign campaign_end confirm:sim - encerrar campanha permanentemente\n"
    "- /campaign info - ver estado completo\n"
    "- /undo - desfazer ultima acao (GM pode desfazer acoes de qualquer jogador)"
)

HELP_JOGADOR = (
    "Comandos de jogador.\n"
    "\n"
    "Rolagem:\n"
    "- /roll dice:1d8 1d10 1d6 - rolar pool de dados\n"
    "- /roll dice:1d8 1d10 include:\"Big Wrench\" - incluir asset na pool\n"
    "- /roll dice:1d8 1d10 extra:1d6 - comprar dado extra com PP (custa 1 PP por dado)\n"
    "- /roll dice:1d8 1d10 difficulty:12 - rolar contra dificuldade\n"
    "\n"
    "Assets:\n"
    "- /asset add name:\"Big Wrench\" die:d6 - criar asset para voce\n"
    "- /asset stepup name:\"Big Wrench\" - step up do asset\n"
    "- /asset stepdown name:\"Big Wrench\" - step down do asset\n"
    "- /asset remove name:\"Big Wrench\" - remover asset\n"
    "\n"
    "Plot Points:\n"
    "- /pp add amount:1 - ganhar PP\n"
    "- /pp remove amount:1 - gastar PP\n"
    "\n"
    "Complications:\n"
    "- /complication add name:\"Broken Arm\" die:d6 - criar complication\n"
    "- /complication stepdown name:\"Broken Arm\" - step down\n"
    "\n"
    "Informacao:\n"
    "- /campaign info - ver estado da campanha e seus dados\n"
    "- /scene info - ver estado da cena atual"
)

HELP_ROLAGEM = (
    "Referencia de rolagem Cortex Prime.\n"
    "\n"
    "Notacao de dados: use dX ou NdX onde X e 4, 6, 8, 10 ou 12.\n"
    "Exemplos: d8, 1d10, 2d6. Separe dados por espaco: 1d8 1d10 2d6.\n"
    "\n"
    "Include: adicione assets a pool pelo nome.\n"
    "Exemplo: /roll dice:1d8 1d10 include:\"Sword\"\n"
    "O dado do asset e adicionado automaticamente a pool.\n"
    "\n"
    "Extra: compre dados extras gastando PP (1 PP por dado).\n"
    "Exemplo: /roll dice:1d8 1d10 extra:1d6\n"
    "\n"
    "Dificuldade: compare o total contra um numero alvo.\n"
    "Exemplo: /roll dice:1d8 1d10 difficulty:10\n"
    "Resultado indica sucesso (margem) ou falha (quanto faltou).\n"
    "\n"
    "Hitches: dados que tiram 1 sao hitches. Nao contam para o total.\n"
    "GM pode dar 1 PP ao jogador e criar complication d6, ou adicionar dado ao Doom Pool.\n"
    "\n"
    "Botch: se todos os dados forem 1, e botch. Total zero.\n"
    "GM cria complication d6 gratis, step up por hitch adicional.\n"
    "\n"
    "Best mode: quando habilitado, o bot calcula as melhores combinacoes de 2 dados.\n"
    "Mostra melhor total e melhor effect die como opcoes pre-calculadas.\n"
    "\n"
    "Effect die: o terceiro maior dado (nao usado no total) define o effect die.\n"
    "Se nao houver terceiro dado, default e d4.\n"
    "\n"
    "Heroic success: margem de 5+ sobre a dificuldade.\n"
    "Effect die faz step up uma vez a cada 5 pontos de margem."
)

HELP_TOPICS = {
    "geral": HELP_GERAL,
    "gm": HELP_GM,
    "jogador": HELP_JOGADOR,
    "rolagem": HELP_ROLAGEM,
}


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="help", description="Referencia de comandos do bot.")
    @app_commands.describe(topic="Topico de ajuda")
    @app_commands.choices(
        topic=[
            app_commands.Choice(name="geral", value="geral"),
            app_commands.Choice(name="gm", value="gm"),
            app_commands.Choice(name="jogador", value="jogador"),
            app_commands.Choice(name="rolagem", value="rolagem"),
        ],
    )
    async def help_command(
        self,
        interaction: Interaction,
        topic: app_commands.Choice[str] | None = None,
    ) -> None:
        key = topic.value if topic else "geral"
        text = HELP_TOPICS[key]
        await interaction.response.send_message(text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
