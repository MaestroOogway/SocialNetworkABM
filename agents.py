from mesa.discrete_space import CellAgent
from commons.commons import *

import random
from typing import Optional, List

PARTY = ['A', 'B']
POLARITYNEWS = [-1, 1]
VERACITYNEWS = [False, True]
PHI = 0.6
ALPHA = 0.05

class News:
    count = 0
    def __init__(
        self,
        id = None,
        party = None,
        polarity = None,
        veracity = None
    ):
        super().__init__() #Initialize News
        if id is None:         
            id = News.count
        self.id = id
        News.count += 1
        self.party = party if party is not None else "A" #random.choice(PARTY)
        self.polarity = polarity if polarity is not None else random.choice(POLARITYNEWS)
        self.veracity = veracity if veracity is not None else random.choice(VERACITYNEWS)

class BOT(CellAgent):
    count = 0
    def __init__(
        self,
        model,
        id = None,
        initialnews = None,
        cell = None
    ):
        super().__init__(model) #Initialize News
        if id is None:         
            id = BOT.count
        self.id = id
        BOT.count += 1
        self.initialnews = initialnews if initialnews is not None else []
        self.cell = cell
    
    def create_news(self):
        news = News()
        self.initialnews.append(news)

    def sendNews(self, news: News, radius: int = 1):
        # recorrer celdas vecinas
        for cell in self.cell.neighborhood:
        # recorrer agentes dentro de cada celda vecina
            for agent in cell.agents:
            # asegurarse de que el agente pueda recibir noticias
                if hasattr(agent, "receiveNews") and agent is not self:
                    agent.receiveNews(news)

class User(CellAgent):

    def __init__(
        self,
        model,
        id,
        interest: Optional[float] = None, 
        credibility: Optional[float] = None,
        perception: Optional[dict[str, float]] = None,
        newsShared: Optional[List[News]] = None,
        newsReceived: Optional[List[News]] = None,
        cell = None
    ):
        super().__init__(model) #Initialize Agent

        self.id = id
        self.interest = interest if interest is not None else random.random()
        self.credibility = credibility
        self.perception = perception if perception is not None else {"A": 0.0, "B": 0.0}
        self.newsShared =  newsShared if newsShared is not None else []
        self.newsReceived =  newsReceived if newsReceived is not None else []
        self.cell = cell

    def computeShareProbability(self, news: News, w_m, w_f, w_c):
        if news.party == 'A':
            return clamp(w_m*news.veracity + w_f*self.perception["A"] + w_c*self.credibility, 0,1)
        elif news.party == 'B':
            return clamp(w_m*news.veracity + w_f*self.perception["B"] + w_c*self.credibility, 0,1)

    def receiveNews(self, news: News):
        self.newsReceived.append(news)
        self.updatePerception(news)

    def sendNews(self, news: News, radius: int = 1):
        # recorrer celdas vecinas 
        for cell in self.cell.neighborhood: 
            # recorrer agentes dentro de cada celda vecina 
            for agent in cell.agents: # asegurarse de que el agente pueda recibir noticias 
                if hasattr(agent, "receiveNews") and agent is not self: 
                    agent.receiveNews(news)


    def shareDecision(self, news: News) -> bool:
        """Abstracto: devolver True si decide compartir (según la noticia)."""
        raise NotImplementedError

    def updatePerception(self, news: News):
        """Abstracto: actualizar percepción según la noticia."""
        raise NotImplementedError

class Susceptible(User):
    def __init__(self, model, id=None, credibility=None, **kwargs):
        if id is None:
            id = len(model.agents_by_type[Susceptible]) if Susceptible in model.agents_by_type else 0
        super().__init__(model, id, credibility=credibility, **kwargs)
        if self.credibility is None:
            self.credibility = random.uniform(0.6, 0.9)

    def shareDecision(self, news: News) -> bool:
        w1 = 0.1 
        w2 = 0.3 
        w3 = 0.6
        pc = self.computeShareProbability(news, w1, w2, w3)
        return random.random() < pc

    def updatePerception(self, news: News):
        if news.party == 'A':
            self.perception["A"] = roundto(clamp(self.perception["A"] + (ALPHA * news.polarity), -1.0, 1.0))
        else:
            self.perception["B"] = roundto(clamp(self.perception["B"] + (ALPHA * news.polarity), -1.0, 1.0))


class Skeptic(User):
    def __init__(self, model, id=None, credibility=None, **kwargs):
        if id is None:
            id = len(model.agents_by_type[Skeptic]) if Skeptic in model.agents_by_type else 0
        super().__init__(model, id, credibility=credibility, **kwargs)
        if self.credibility is None:
            self.credibility = random.uniform(0.1, 0.3)

    
    def shareDecision(self, news: News) -> bool:
        w1 = 0.3 
        w2 = 0.6 
        w3 = 0.1
        if news.veracity == False:
            return False
        else:
            pc = self.computeShareProbability(news, w1, w2, w3)
            return random.random() < pc

    def updatePerception(self, news: News):
        factor = 1 if news.veracity == True else 0  #if the news is false doesnt sum, only sum if its true
        if news.party == 'A':
            self.perception["A"] = roundto(clamp(self.perception["A"] + (ALPHA * news.polarity * factor), -1.0, 1.0))
        else:
            self.perception["B"] = roundto(clamp(self.perception["B"] + (ALPHA * news.polarity * factor), -1.0, 1.0))
