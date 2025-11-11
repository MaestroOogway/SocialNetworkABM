from model import SocialNetworkModel
from agents import Susceptible, Skeptic, BOT
from mesa.experimental.devs import ABMSimulator
from mesa.visualization import (
    CommandConsole,
    Slider,
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle

def social_network_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
        zorder=2,
        edgecolors="black"
    )

    if isinstance(agent, Susceptible):
        portrayal.update(("color", "red"))
    elif isinstance(agent, Skeptic):
        portrayal.update(("color", "blue"))
    elif isinstance(agent, BOT):
        portrayal.update(("color", "black"))

    return portrayal


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": Slider("Grid Width", 20, 5, 50),
    "height": Slider("Grid Height", 20, 5, 50),
    "n_susceptible": Slider("Initial Susceptible Users", 10, 1, 200),
    "n_skeptic": Slider("Initial Skeptic Users", 10, 1, 200),
}

def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([x + 0.5 for x in range(model.grid.width)])
    ax.set_yticks([y + 0.5 for y in range(model.grid.height)])
    ax.set_xlim(-0.5, model.grid.width - 0.5)
    ax.set_ylim(-0.5, model.grid.height - 0.5)
    ax.grid(True, which="both", color="lightgray", linewidth=0.5)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)


def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))

    
perceptionbyagent = make_plot_component(
    {"AvgPerception_Skeptic": "tab:blue", "AvgPerception_Susceptible": "tab:red"}
)

sharednews = make_plot_component(
    {"TrueNewsShared": "tab:blue", "FalseNewsShared": "tab:red"}
)

simulator = ABMSimulator()
model = SocialNetworkModel(simulator=simulator)

renderer = SpaceRenderer(
    model,
    backend="matplotlib",
)
renderer.draw_agents(social_network_portrayal)
renderer.post_process = post_process_space

page = SolaraViz(
    model,
    renderer,
    components=[perceptionbyagent, sharednews, CommandConsole],
    model_params=model_params,
    name="Social Network Simulation",
    simulator=simulator,
)
page  # noqa