#!/usr/bin/env python3
import os
import json
import datetime

# Caminho para o arquivo de dados
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")
GAME_STATE_FILE = os.path.join(DATA_DIR, "game_state.json")

def ensure_data_dir_exists():
    """Garante que o diretório de dados exista"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_high_scores(players_scores):
    """
    Salva as pontuações dos jogadores no arquivo de pontuação.
    
    Args:
        players_scores: Lista de dicionários com pontuações dos jogadores
        [{'name': 'Player1', 'score': 5}, {'name': 'Player2', 'score': 3}]
    """
    ensure_data_dir_exists()
    
    # Carregar scores existentes
    existing_scores = load_high_scores()
    
    # Adicionar novos scores
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for player in players_scores:
        player['timestamp'] = timestamp
        existing_scores.append(player)
    
    # Ordenar por pontuação (do maior para o menor)
    existing_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Manter apenas os top 10 scores
    top_scores = existing_scores[:10]
    
    # Salvar no arquivo
    with open(SCORES_FILE, 'w') as f:
        json.dump(top_scores, f, indent=2)
    
    return top_scores

def load_high_scores():
    """Carrega as pontuações salvas do arquivo"""
    ensure_data_dir_exists()
    
    if not os.path.exists(SCORES_FILE):
        return []
    
    try:
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Se o arquivo estiver corrompido ou não existir, retorna uma lista vazia
        return []

def save_game_state(state):
    """
    Salva o estado atual do jogo para continuar depois
    
    Args:
        state: Dicionário com o estado do jogo
        {
            'players': [{'name': 'Player1'}, {'name': 'Player2'}],
            'scores': [3, 2],
            'turn': 0,
            'buildings': [...],
            'gravity': 300
        }
    """
    ensure_data_dir_exists()
    
    # Adicionar timestamp
    state['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(GAME_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_game_state():
    """Carrega o estado salvo do jogo"""
    ensure_data_dir_exists()
    
    if not os.path.exists(GAME_STATE_FILE):
        return None
    
    try:
        with open(GAME_STATE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Se o arquivo estiver corrompido ou não existir, retorna None
        return None

def delete_game_state():
    """Remove o arquivo de estado do jogo"""
    if os.path.exists(GAME_STATE_FILE):
        os.remove(GAME_STATE_FILE)
