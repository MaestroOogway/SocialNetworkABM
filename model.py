import math
import random
from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector
from mesa.experimental.devs import ABMSimulator

from agents import BOT, Skeptic, Susceptible, NewsReel


class SocialNetworkModel(Model):
    def __init__(
        self,
        width=20,
        height=20,
        n_susceptible=70,
        n_skeptic=70,
        n_bots=5,
        n_newsreel=5,
        seed=None,
        simulator: ABMSimulator = None,
    ):
        super().__init__(seed=seed)
        
        # Si no se proporciona simulador, crear uno nuevo
        if simulator is None:
            simulator = ABMSimulator()
        
        self.simulator = simulator
        self.simulator.setup(self)

        self.height = height
        self.width = width
        self.running = True
        self.true_news_shared = 0
        self.false_news_shared = 0
        self.conversions_to_skeptic = 0
        self.conversions_to_susceptible = 0
        self.previous_conversions = 0  # Rastrear conversiones previas para detectar cambios
        self.converted_agents = []  # Lista para almacenar detalles de agentes convertidos
        self.news_propagation = []  # Lista para rastrear quién comparte a quién en cada step

        self.grid = OrthogonalMooreGrid(
            [self.height, self.width],
            torus=True,
            capacity=1,  # Máximo 1 agente por celda
            random=self.random,
        )

        # Obtener todas las celdas disponibles y mezclarlas
        available_cells = list(self.grid.all_cells.cells)
        self.random.shuffle(available_cells)

        # Verificar que hay suficientes celdas
        total_agents = n_skeptic + n_susceptible + n_bots + n_newsreel
        if total_agents > len(available_cells):
            raise ValueError(f"No hay suficientes celdas ({len(available_cells)}) para {total_agents} agentes")

        cell_index = 0

        # Crear agentes asignando celdas únicas
        Skeptic.create_agents(
            self,
            n_skeptic,
            cell=available_cells[cell_index : cell_index + n_skeptic],
        )
        cell_index += n_skeptic

        Susceptible.create_agents(
            self,
            n_susceptible,
            cell=available_cells[cell_index : cell_index + n_susceptible],
        )
        cell_index += n_susceptible

        BOT.create_agents(
            self,
            n_bots,
            cell=available_cells[cell_index : cell_index + n_bots],
        )
        cell_index += n_bots

        NewsReel.create_agents(
            self,
            n_newsreel,
            cell=available_cells[cell_index : cell_index + n_newsreel],
        )

        # Guardar todos los agentes en una sola lista
        self.total_agents = list(self.agents_by_type[BOT]) + list(self.agents_by_type[NewsReel]) + list(self.agents_by_type[Skeptic]) + list(self.agents_by_type[Susceptible])

        # NUEVA FUNCIÓN
        def avg_perception_by_agent(m, party: str):
            """Calcula el promedio de percepción hacia un partido,
            separado por tipo de agente (Skeptic y Susceptible)."""
            user_agents = [a for a in m.total_agents if hasattr(a, "perception") and isinstance(a.perception, dict)]

            if not user_agents:
                return {"Skeptic": 0.0, "Susceptible": 0.0}

            skeptics = [a for a in user_agents if isinstance(a, Skeptic)]
            susceptibles = [a for a in user_agents if isinstance(a, Susceptible)]

            def mean(values):
                return sum(values) / len(values) if values else 0.0

            avg_skeptic = mean([a.perception[party] for a in skeptics])
            avg_susceptible = mean([a.perception[party] for a in susceptibles])

            return {"Skeptic": avg_skeptic, "Susceptible": avg_susceptible}

        #  DATA COLLECTOR
        self.datacollector = DataCollector(
            model_reporters={
                "AvgPerception_Skeptic": lambda m: avg_perception_by_agent(m, "A")["Skeptic"],
                "AvgPerception_Susceptible": lambda m: avg_perception_by_agent(m, "A")["Susceptible"],
                "TrueNewsShared": lambda m: m.true_news_shared,
                "FalseNewsShared": lambda m: m.false_news_shared,
                "NumSkeptics": lambda m: len(m.agents_by_type[Skeptic]),
                "NumSusceptibles": lambda m: len(m.agents_by_type[Susceptible]),
                "ConversionsToSkeptic": lambda m: m.conversions_to_skeptic,
                "ConversionsToSusceptible": lambda m: m.conversions_to_susceptible,
            }
        )

        # Inicialización: bots crean y envían noticias
        print(f"\n{'='*60}")
        print("INICIALIZACIÓN DEL MODELO")
        print(f"{'='*60}")
        print(f"Grid: {self.width}x{self.height}")
        print(f"Skeptics: {n_skeptic}")
        print(f"Susceptibles: {n_susceptible}")
        print(f"BOTs: {n_bots}")
        print(f"NewsReels: {n_newsreel}")

        for bot in self.agents_by_type[BOT]:
            bot.create_news()
            for news in list(bot.initialnews):
                bot.sendNews(news, radius=1)

        for newsreel in self.agents_by_type[NewsReel]:
            newsreel.create_news()
            for news in list(newsreel.initialnews):
                newsreel.sendNews(news, radius=1)

        # Colecta inicial
        self.datacollector.collect(self)

    def step(self):
        """Ejecuta un paso de la simulación: cada usuario decide si compartir sus noticias."""
        # Limpiar propagaciones del step ANTERIOR al INICIO del nuevo step
        self.news_propagation.clear()

        user_agents = list(self.agents_by_type[Skeptic]) + list(self.agents_by_type[Susceptible])

        news_shared_this_step = 0

        for agent in user_agents:
            for news in list(agent.newsReceived):
                if agent.shareDecision(news):
                    self.countNewsbyType(news)
                    agent.sendNews(news, radius=1)
                    news_shared_this_step += 1

        # Verificar si hubo conversiones en este step
        total_conversions = self.conversions_to_skeptic + self.conversions_to_susceptible
        if total_conversions > self.previous_conversions:
            if self.converted_agents:
                self.converted_agents.clear()
            self.previous_conversions = total_conversions

        self.datacollector.collect(self)

        # NO limpiar aquí - las propagaciones deben persistir para visualización
        # Se limpian al INICIO del próximo step

    def countNewsbyType(self, news):
        """Incrementa los contadores globales de noticias según su veracidad."""
        if news.veracity:
            self.true_news_shared += 1
        else:
            self.false_news_shared += 1
