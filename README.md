#  OrbitSpace — Backend

Backend del TFG **OrbitSpace**: plataforma web para la gestión y visualización de satélites y misiones espaciales con asistente de inteligencia artificial integrado.

🌐 **Demo en vivo:** [orbitspace.vercel.app](https://orbitspace.vercel.app)

---

##  ¿Qué es OrbitSpace?

Aplicación web full-stack que permite consultar información sobre satélites y misiones espaciales de forma intuitiva, orientada a usuarios sin conocimientos técnicos. Incluye un asistente virtual con IA para resolver dudas en tiempo real sobre terminología y telemetría espacial.

---

##  Arquitectura del sistema
Arquitectura desacoplada cliente-servidor en tres capas:

- **Frontend** — React + Tailwind CSS + React Router DOM (SPA)
- **Backend** — Python + FastAPI (API RESTful asíncrona)
- **Base de datos** — MySQL relacional normalizado (7 entidades)
- **IA** — Integración con OpenRouter API para el asistente virtual

---

##  Tecnologías

| Capa | Tecnología |
|---|---|
| Frontend | React, Tailwind CSS, React Router DOM |
| Backend | Python, FastAPI |
| Base de datos | MySQL |
| Inteligencia Artificial | OpenRouter API |
| Autenticación | JWT (JSON Web Tokens) |
| Despliegue | Vercel (frontend) · Render (backend) |
| Gestión del proyecto | Git, GitHub, Scrum Board |

---

## Funcionalidades principales

-  Registro e inicio de sesión con autenticación JWT
-  Visualización de satélites activos con datos en tiempo real
-  Mapa orbital interactivo (barrido LEO/MEO)
-  Historial y seguimiento de lanzamientos espaciales
-  Sistema de favoritos por usuario
-  Alertas de próximos lanzamientos
-  Asistente virtual IA para consultas sobre telemetría y misiones
-  Filtrado por agencia, tipo de misión y año

---

##  Diseño de base de datos

Modelo relacional con 7 entidades: `usuario`, `misión`, `vehículo`, `organización`, `lanzamiento`, `favorito`, `alerta`.

---

##  Equipo

Proyecto desarrollado como TFG del ciclo **Desarrollo de Aplicaciones Web** en la Universidad Europea — Centro Profesional (2025-2026).

- **Angelina Lepeshko** — [GitHub](https://github.com/Argenika) · [LinkedIn](https://www.linkedin.com/in/angelina-lepeshko-b9a410329/)
