# app.py
from mesa.visualization import CommandConsole, Slider, SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle, make_plot_component
import matplotlib.patches as patches
from model import SocialNetworkModel
from agents import Susceptible, Skeptic

# ---------------------------
# Portrayal de los agentes
# ---------------------------
def user_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=20,
        marker="o",
        zorder=2,
        alpha=1.0,
        edgecolors="k",
        linewidths=1.2,
    )

    if isinstance(agent, Susceptible):
        portrayal.update(("color", "tab:blue"))
    elif isinstance(agent, Skeptic):
        portrayal.update(("color", "tab:red"))

    return portrayal

# ---------------------------
# Parámetros ajustables
# ---------------------------
model_params = {
    "width": Slider("Grid Width", 20, 5, 50),
    "height": Slider("Grid Height", 20, 5, 50),
    "n_susceptible": Slider("Initial Susceptible Users", 10, 1, 200),
    "n_skeptic": Slider("Initial Skeptic Users", 10, 1, 200),
    "n_initial_news": Slider("Initial News", 5, 0, 50),
}

# ---------------------------
# Instancia del modelo
# ---------------------------
init_kwargs = {k: v.value if hasattr(v, 'value') else v for k, v in model_params.items()}
model_instance = SocialNetworkModel(**init_kwargs)

# ---------------------------
# Configuración del renderer
# ---------------------------
renderer = SpaceRenderer(model_instance, backend="matplotlib")
renderer.draw_agents(user_portrayal)

def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_facecolor("white")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-0.5, model_instance.width - 0.5)
    ax.set_ylim(-0.5, model_instance.height - 0.5)
    ax.invert_yaxis()

    # ocultar spines exteriores
    for spine in ax.spines.values():
        spine.set_visible(False)

    # dibujar borde de celda según agente (una rect por celda ocupada)
    cell_map = {}
    for agent in model_instance.user_agents:
        if not hasattr(agent, "pos"):
            continue
        pos = agent.pos
        cell_map.setdefault(pos, []).append(agent)

    for (x, y), agents_in_cell in cell_map.items():
        if all(isinstance(a, Susceptible) for a in agents_in_cell):
            edge_color = "tab:blue"
        elif all(isinstance(a, Skeptic) for a in agents_in_cell):
            edge_color = "tab:red"
        else:
            edge_color = "k"

        rect = patches.Rectangle(
            (x - 0.5, y - 0.5),
            1.0,
            1.0,
            linewidth=2.0,
            edgecolor=edge_color,
            facecolor="none",
            zorder=3
        )
        ax.add_patch(rect)

renderer.post_process = post_process_space

# ---------------------------
# Componentes de gráficos
# ---------------------------
lineplot_component = make_plot_component(
    {"Susceptible Shared": "tab:blue", "Skeptic Shared": "tab:red"}
)

# Mostrar percepción media por partido (estas claves vienen de model_reporters)
perception_by_party = make_plot_component(
    {"AvgPerception_A": "tab:blue", "AvgPerception_B": "tab:red"}
)

# ---------------------------
# Página de Solara
# ---------------------------
page = SolaraViz(
    model_instance,
    renderer,
    components=[lineplot_component, perception_by_party, CommandConsole],
    model_params=model_params,
    name="Social Network ABM",
)

page  # noqa
