Social Network ABM

Simulación de difusión de noticias en una red social usando agentes autónomos con comportamientos distintos: Susceptible y Skeptic.
El modelo está implementado en Python usando Mesa
 y Solara
 para la visualización interactiva.

Características

Grilla bidimensional de tamaño configurable, donde los agentes interactúan con vecinos inmediatos.

Agentes con percepción, credibilidad y decisiones de compartir noticias según su tipo.

Noticias iniciales asignadas a agentes aleatorios para simular difusión.

Métricas recolectadas durante la simulación:

Percepción promedio de los usuarios

Noticias compartidas totales

Noticias compartidas por tipo de agente

Instalación

Clonar el repositorio:

git clone https://github.com/MaestroOogway/SocialNetworkABM.git
cd SocialNetwork-ABM

Instalar dependencias:

pip install mesa solara matplotlib

Uso

Ejecuta la interfaz interactiva:

solara run app.py


Luego abre el navegador en la URL que te indica la consola (por defecto http://localhost:8765).

Ajusta los parámetros del modelo (cantidad de agentes, tamaño de grilla, noticias iniciales) desde la UI.

Visualiza el espacio de agentes y las métricas en tiempo real.

Estructura del proyecto
SocialNetwork-ABM/
├── agents.py         # Clases de agentes: Susceptible, Skeptic, News
├── model.py          # Definición del modelo y reglas de interacción
├── app.py            # Interfaz y visualización con Solara
├── README.md         # Este archivo