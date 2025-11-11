import math
import random
from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector
from mesa.experimental.devs import ABMSimulator

from agents import BOT, Skeptic, Susceptible


class SocialNetworkModel(Model):
    def __init__(
        self,
        width=20,
        height=20,
        n_susceptible=30,
        n_skeptic=30,
        n_bots=6,
        seed=None,
        simulator: ABMSimulator = None,
    ):
        super().__init__(seed=seed)
        self.simulator = simulator
        self.simulator.setup(self)

        self.height = height
        self.width = width
        self.running = True
        self.true_news_shared = 0
        self.false_news_shared = 0

        self.grid = OrthogonalMooreGrid(
            [self.height, self.width],
            torus=True,
            capacity=math.inf,
            random=self.random,
        )

        # Crear agentes
        Skeptic.create_agents(
            self,
            n_skeptic,
            cell=self.random.choices(self.grid.all_cells.cells, k=n_skeptic),
        )

        Susceptible.create_agents(
            self,
            n_susceptible,
            cell=self.random.choices(self.grid.all_cells.cells, k=n_susceptible),
        )

        BOT.create_agents(
            self,
            n_bots,
            cell=self.random.choices(self.grid.all_cells.cells, k=n_bots),
        )

        # Guardar todos los agentes en una sola lista
        self.total_agents = (
            list(self.agents_by_type[BOT])
            + list(self.agents_by_type[Skeptic])
            + list(self.agents_by_type[Susceptible])
        )

        # --- NUEVA FUNCIÓN ---
        def avg_perception_by_agent(m, party: str):
            """Calcula el promedio de percepción hacia un partido,
            separado por tipo de agente (Skeptic y Susceptible)."""
            user_agents = [
                a for a in m.total_agents
                if hasattr(a, "perception") and isinstance(a.perception, dict)
            ]

            if not user_agents:
                return {"Skeptic": 0.0, "Susceptible": 0.0}

            skeptics = [a for a in user_agents if isinstance(a, Skeptic)]
            susceptibles = [a for a in user_agents if isinstance(a, Susceptible)]

            def mean(values):
                return sum(values) / len(values) if values else 0.0

            avg_skeptic = mean([a.perception[party] for a in skeptics])
            avg_susceptible = mean([a.perception[party] for a in susceptibles])

            return {"Skeptic": avg_skeptic, "Susceptible": avg_susceptible}

        # --- DATA COLLECTOR ---
        self.datacollector = DataCollector(
            model_reporters={
                "AvgPerception_Skeptic": lambda m: avg_perception_by_agent(m, "A")["Skeptic"],
                "AvgPerception_Susceptible": lambda m: avg_perception_by_agent(m, "A")["Susceptible"],
                "TrueNewsShared": lambda m: m.true_news_shared,
                "FalseNewsShared": lambda m: m.false_news_shared,
            }
        )

        # --- Inicialización: bots crean y envían noticias ---
        for bot in self.agents_by_type[BOT]:
            bot.create_news()
            for news in list(bot.initialnews):
                bot.sendNews(news, radius=1)

        # Colecta inicial
        self.datacollector.collect(self)

    def step(self):
        """Ejecuta un paso de la simulación: cada usuario decide si compartir sus noticias."""
        user_agents = list(self.agents_by_type[Skeptic]) + list(self.agents_by_type[Susceptible])

        for agent in user_agents:
            for news in list(agent.newsReceived):
                if agent.shareDecision(news):
                    self.countNewsbyType(news)
                    agent.sendNews(news, radius=1)

        self.datacollector.collect(self)

    def countNewsbyType(self, news):
        """Incrementa los contadores globales de noticias según su veracidad."""
        if news.veracity:
            self.true_news_shared += 1
        else:
            self.false_news_shared += 1
