from model import SocialNetworkModel
from agents import Susceptible, Skeptic, BOT, NewsReel
from mesa.experimental.devs import ABMSimulator
from mesa.visualization import (
    CommandConsole,
    Slider,
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle
import solara
from matplotlib.figure import Figure


def social_network_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(size=50, marker="o", zorder=2, edgecolors="black")

    if isinstance(agent, Susceptible):
        portrayal.update(("color", "red"))
    elif isinstance(agent, Skeptic):
        portrayal.update(("color", "blue"))
    elif isinstance(agent, BOT):
        portrayal.update(("color", "black"))
    elif isinstance(agent, NewsReel):
        portrayal.update(("color", "white"))

    return portrayal


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": Slider("Grid Width", 20, 5, 50),
    "height": Slider("Grid Height", 20, 5, 50),
    "n_susceptible": Slider("Initial Susceptible Users", 70, 1, 200),
    "n_skeptic": Slider("Initial Skeptic Users", 70, 1, 200),
}


def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))


# Crear los componentes de gráficos una sola vez
perception_plot = make_plot_component({"AvgPerception_Skeptic": "tab:blue", "AvgPerception_Susceptible": "tab:red"})
shared_news_plot = make_plot_component({"TrueNewsShared": "tab:blue", "FalseNewsShared": "tab:red"})


@solara.component
def SpaceWithArrows(model):
    """Componente personalizado para el espacio con flechas dinámicas"""
    # Verificar que model es una instancia, no la clase
    if not hasattr(model, "width"):
        return solara.Text("Waiting for model initialization...")

    # Usar model.steps como dependencia para forzar re-render
    steps = model.steps

    fig = Figure(figsize=(8, 8))
    ax = fig.add_subplot(111)

    # Dibujar grid
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, model.width - 0.5)
    ax.set_ylim(-0.5, model.height - 0.5)
    ax.set_xticks([x + 0.5 for x in range(model.width)])
    ax.set_yticks([y + 0.5 for y in range(model.height)])
    ax.grid(True, which="both", color="lightgray", linewidth=0.5)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # Dibujar agentes
    for agent in model.agents:
        if hasattr(agent, "cell") and hasattr(agent.cell, "coordinate"):
            portrayal = social_network_portrayal(agent)
            if portrayal:
                x, y = agent.cell.coordinate
                ax.scatter(
                    x,
                    y,
                    s=portrayal.size if hasattr(portrayal, "size") else 50,
                    c=portrayal.color if hasattr(portrayal, "color") else "gray",
                    marker=portrayal.marker if hasattr(portrayal, "marker") else "o",
                    edgecolors=portrayal.edgecolors if hasattr(portrayal, "edgecolors") else "black",
                    zorder=portrayal.zorder if hasattr(portrayal, "zorder") else 2,
                )

    # Dibujar flechas de propagación
    if hasattr(model, "news_propagation") and model.news_propagation:
        agent_positions = {}
        for agent in model.agents:
            if hasattr(agent, "cell") and hasattr(agent.cell, "coordinate"):
                agent_positions[agent.id] = agent.cell.coordinate

        for prop in model.news_propagation:
            sender_id = prop["sender_id"]
            receiver_id = prop["receiver_id"]

            if sender_id in agent_positions and receiver_id in agent_positions:
                sender_pos = agent_positions[sender_id]
                receiver_pos = agent_positions[receiver_id]

                arrow_color = "green" if prop["news_veracity"] else "red"

                ax.annotate(
                    "",
                    xy=receiver_pos,
                    xytext=sender_pos,
                    arrowprops=dict(
                        arrowstyle="->",
                        color=arrow_color,
                        alpha=0.7,
                        lw=2.5,
                        shrinkA=8,
                        shrinkB=8,
                    ),
                )

    solara.FigureMatplotlib(fig, dependencies=[steps, id(model)])


simulator = ABMSimulator()
model = SocialNetworkModel(simulator=simulator)


@solara.component
def Page():
    return SolaraViz(
        model,
        components=[SpaceWithArrows, perception_plot, shared_news_plot, CommandConsole],
        model_params=model_params,
        name="Social Network Simulation",
    )


page = Page
