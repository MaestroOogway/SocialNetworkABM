from mesa.discrete_space import CellAgent, FixedAgent
from commons.commons import *

import random
from typing import Optional, List

PARTY = ['A', 'B']
POLARITYNEWS = [-1, 1]
PHI = 0.6
ALPHA = 0.05

def clamp(x: float, a: float, b: float) -> float:
    return max(a, min(b, x))

class News:
    def __init__(
        self,
        id,
        party: Optional[str] = None,
        polarity: Optional[int] = None,
        veracity: Optional[float] = None
    ):
        self.id = id
        self.party = party if party is not None else random.choice(PARTY)
        self.polarity = polarity if polarity is not None else random.choice(POLARITYNEWS)
        self.veracity = veracity if veracity is not None else round(random.uniform(0.01, 0.99), 2)

class User(CellAgent):
    """Initialize an user social Network. 
    Args: 
    model: Model instance 
    id: id of the user state: actual state of the user. 
    politicalParty: if the user belongs to "a" or "b" party 
    credibility: numerical index of credibility of the user, depends of the user skeptic has 0.1 to 0.3 and suceptible has 0.7 to 1 
    percpetion: numerical index of percpetion of the user. satarts in zero(neutral), next in the advance of simualtion goes to -1 or 1. 
    newsShared: number of news shared on the network 
    newsReceived: numbers of news recived on te network """

    def __init__(
        self,
        model,
        id,
        politicalParty: Optional[str] = None,
        credibility: Optional[float] = None,
        perception: float = 0.0,
        newsShared: Optional[List[News]] = None,
        newsReceived: Optional[List[News]] = None,
        cell = None
    ):
        """
        Initialize a user in the social network.
        """
        super().__init__(model)

        self.id = id
        self.politicalParty = politicalParty if politicalParty is not None else random.choice(PARTY)
        self.credibility = credibility
        self.perception = perception
        self.newsShared: List[News] = newsShared if newsShared is not None else []
        self.newsReceived: List[News] = newsReceived if newsReceived is not None else []

    def computeShareProbability(self, news: News, w_m, w_f, w_c):
        party_agent = 1 if self.politicalParty=="A" else -1
        party_news = 1 if news.party=="A" else -1
        m = (1 + news.polarity*party_news*party_agent)/2
        return clamp(w_m*m + w_f*news.veracity + w_c*self.credibility, 0,1)

    def receiveNews(self, news: News):
        self.newsReceived.append(news)
        self.updatePerception(news)

    def sendNews(self, news: News, radius: int = 1):
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=True,          
            include_center=False, 
            radius=radius
        )
    
        for agent in neighbors:
            agent.receiveNews(news)

        self.newsShared.append(news)

    def shareDecision(self, news: News) -> bool:
        """Abstracto: devolver True si decide compartir (según la noticia)."""
        raise NotImplementedError


    def updatePerception(self, news: News):
        """Abstracto: actualizar percepción según la noticia."""
        raise NotImplementedError


class Susceptible(User):
    def __init__(self, model, id, credibility=None, **kwargs):
        super().__init__(model, id, credibility=credibility, **kwargs)
        if self.credibility is None:
            self.credibility = random.uniform(0.6, 0.9)

    def shareDecision(self, news: News) -> bool:
        w1 = 0.5 
        w2 = 0.3 
        w3 = 0.2
        pc = self.computeShareProbability(news, w1, w2, w3)
        return random.random() < pc

    def updatePerception(self, news: News):
        """Update in function to news recived"""
        if (self.politicalParty == news.party):
            x = 0.0 
        else:
            x = 1.0
        self.perception = clamp(self.perception + x * ALPHA * news.polarity, -1.0, 1.0)



class Skeptic(User):
    def __init__(self, model, id, credibility=None, **kwargs):
        super().__init__(model, id, credibility=credibility, **kwargs)
        if self.credibility is None:
            self.credibility = random.uniform(0.1, 0.3)
    
    def shareDecision(self, news: News) -> bool:
        w1 = 0.1 
        w2 = 0.6 
        w3 = 0.3
        pc = self.computeShareProbability(news, w1, w2, w3)
        return random.random() < pc

    def updatePerception(self, news: News):
        """Update in function to news recived."""
        if (self.politicalParty == news.party):
            x = 0.0 
        else:
            x = 1.0
        self.perception = clamp(self.perception + x * ALPHA * news.polarity, -1.0, 1.0)
