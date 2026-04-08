import asyncio
import websockets
import json

# Dicionários de estado global
rooms = {}
player_data = {}

async def handler(websocket):
    room_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "join":
                room_id = data["room"]
                p_id = data.get("id", "??")
                player_data[websocket] = p_id
                
                if room_id not in rooms:
                    rooms[room_id] = []
                
                # Sincronização de IDs: Todo mundo se conhece
                for client in rooms[room_id]:
                    # Veterano avisa o novato que ele existe
                    veteran_id = player_data.get(client, "??")
                    await websocket.send(json.dumps({"type": "player_joined", "id": veteran_id}))
                    # Novato avisa o veterano que ele chegou
                    await client.send(json.dumps({"type": "player_joined", "id": p_id}))
                    
                rooms[room_id].append(websocket)
                print(f"Jogador {p_id} entrou na sala: {room_id}")

            # Repassa QUALQUER mensagem da sala para os outros jogadores
            elif room_id:
                if room_id in rooms:
                    message_to_send = json.dumps(data)
                    for client in rooms[room_id]:
                        if client != websocket:
                            await client.send(message_to_send)
    except:
        pass
    finally:
        # Remover o jogador da sala ao desconectar
        if room_id in rooms and websocket in rooms[room_id]:
            rooms[room_id].remove(websocket)
            if not rooms[room_id]:
                del rooms[room_id]
        print("Jogador desconectado")

async def main():
    import os
    # O Render exige que usemos a porta da variável de ambiente PORT
    port = int(os.environ.get("PORT", 8080))
    async with websockets.serve(handler, "0.0.0.0", port, origins=None):
        print(f"Servidor de Doom Multiplayer rodando na porta {port}...")
        await asyncio.Future()  # roda para sempre

if __name__ == "__main__":
    asyncio.run(main())
