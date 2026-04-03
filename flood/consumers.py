import json
from channels.generic.websocket import AsyncWebsocketConsumer


class FloodConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('flood_alerts', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('flood_alerts', self.channel_name)

    async def flood_alert(self, event):
        await self.send(text_data=json.dumps(event['data']))
