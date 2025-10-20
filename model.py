# model.py
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import Susceptible, Skeptic, News
import random

class SocialNetworkModel(Model):
    def __init__(self, width=20, height=20, n_susceptible=20, n_skeptic=10, n_initial_news=5):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=True)

        # NO usar self.agents 
        self.user_agents = []

        # Crear agentes susceptibles
        for i in range(n_susceptible):
            agent = Susceptible(self, id=f"S{i}")
            self.user_agents.append(agent)
            x, y = random.randrange(width), random.randrange(height)
            self.grid.place_agent(agent, (x, y))

        # Crear agentes escépticos
        for i in range(n_skeptic):
            agent = Skeptic(self, id=f"K{i}")
            self.user_agents.append(agent)
            x, y = random.randrange(width), random.randrange(height)
            self.grid.place_agent(agent, (x, y))

        # Inicializar noticias
        self.seed_news(n_initial_news)


        def avg_perception(m):
            if len(m.user_agents) == 0:
                return 0.0
            return sum(a.perception for a in m.user_agents) / len(m.user_agents)

        def avg_perception_party(m, party):
            agents = [a for a in m.user_agents if a.politicalParty == party]
            if not agents:
                return 0.0
            return sum(a.perception for a in agents) / len(agents)

        def total_news_shared(m):
            return sum(len(a.newsShared) for a in m.user_agents)

        def susceptible_shared(m):
            # suma de noticias compartidas por agentes Susceptible
            return sum(len(a.newsShared) for a in m.user_agents if isinstance(a, Susceptible))

        def skeptic_shared(m):
            # suma de noticias compartidas por agentes Skeptic
            return sum(len(a.newsShared) for a in m.user_agents if isinstance(a, Skeptic))

        self.datacollector = DataCollector(
            model_reporters={
                "AvgPerception": avg_perception,
                "AvgPerception_A": lambda m: avg_perception_party(m, "A"),
                "AvgPerception_B": lambda m: avg_perception_party(m, "B"),
                "TotalNewsShared": total_news_shared,
                "Susceptible Shared": susceptible_shared,
                "Skeptic Shared": skeptic_shared,
            },
            agent_reporters={
                "Perception": lambda a: a.perception,
                "Party": lambda a: a.politicalParty
            }
        )

        self.running = True
        # recolectar estado inicial
        self.datacollector.collect(self)

    def seed_news(self, n_news: int = 5):
        """Crea las noticias iniciales y las asigna a agentes aleatorios."""
        if len(self.user_agents) == 0 or n_news <= 0:
            return
        for i in range(n_news):
            news = News(id=f"N{i}")
            # Asignar la noticia a 1 o 2 agentes al azar para empezar la difusión
            k = min(len(self.user_agents), random.randint(1, 2))
            targets = random.sample(self.user_agents, k=k)
            for agent in targets:
                agent.receiveNews(news)

    def step(self):
        """Ejecuta un paso de la simulación: cada agente decide si comparte sus noticias."""
        # iteramos sobre una copia por si la lista cambia al enviar noticias
        for agent in list(self.user_agents):
            # iterar sobre copia de newsReceived para evitar mutación durante el loop
            for news in list(agent.newsReceived):
                if agent.shareDecision(news):
                    agent.sendNews(news, radius=1)  # compartimos a vecinos inmediatos

        # Recoger métricas
        self.datacollector.collect(self)
