# 🏆 Data Battle IA PAU 2026 – Projet …

## 👥 Équipe
- Nom de l’équipe : Les Animaux Puissants
- Membres :
  - Crahay--Boudou Florent
  - Finana Tom
  - Cassard Pierre-Antoine
  - Carriac Simon
  - Decostanzi Simon
  - Tueux Rubens

## 🎯 Problématique
Aujourd’hui, les systèmes d’alerte d'orages utilisent une règle simple : une alerte reste active pendant 30 minutes après le dernier éclair au sol. 
Cette approche manque de précision et peut entraîner des interruptions inutiles d’activité, notamment dans des environnements critiques comme les aéroports. 
L’objectif est donc de développer un modèle capable d’estimer la probabilité réelle de fin d’un orage lorsqu'un éclair tombe.

## 💡 Solution proposée
Notre Solution repose sur l'utilisation d'un modèle de Gradient Boosting entraîné sur les données de Météorage. 
Il s'agit d'une interface dans laquelle il est possible de choisir un fichier CSV ou de rentrer à la main les données caractéristiques d'un éclair.
Puis le modèle entraîné sort une probabilité que le dernier éclair enregistré marque bien la fin de l'orage.

## ⚙️ Stack technique
- Langages : Python
- Frameworks : FastAPI - Vue.JS 
- Outils : Docker - Pandas
- IA (si utilisé) : Gemini

## 🚀 Installation & exécution

### Prérequis
Python - Docker

### Installation
docker compose up -d --build

### Exécution
Aller sur localhost:67
Depuis l'interface, choisir l'aéroport d'une ville
Puis rentrer les données d'un éclair ou choisir un csv
