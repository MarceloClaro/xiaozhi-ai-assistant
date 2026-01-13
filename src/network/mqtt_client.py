import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(
        self,
        server,
        port,
        username,
        password,
        subscribe_topic,
        publish_topic=None,
        client_id="PythonClient",
        on_connect=None,
        on_message=None,
        on_publish=None,
        on_disconnect=None,
    ):
        """Inicializando MqttClient 。

        :param server: MQTT servidor
        :param port: MQTT servidor
        :param username: usuário
        :param password: 
        :param subscribe_topic: de
        :param publish_topic: de
        :param client_id: cliente ID，para "PythonClient"
        :param on_connect: deConectando
        :param on_message: demensagemRecebendo
        :param on_publish: demensagem
        :param on_disconnect: deDesconectadoConectando
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client_id = client_id

        #  MQTT ，UsandodeAPIVersão
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv5)

        # Configurandoe
        self.client.username_pw_set(self.username, self.password)

        # Configurando，Se，entãoUsandode，entãoUsandode
        if on_connect:
            self.client.on_connect = on_connect
        else:
            self.client.on_connect = self._on_connect

        self.client.on_message = on_message if on_message else self._on_message
        self.client.on_publish = on_publish if on_publish else self._on_publish

        if on_disconnect:
            self.client.on_disconnect = on_disconnect
        else:
            self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """
        deConectando。
        """
        if rc == 0:
            print("✅ SucessoConexãopara MQTT Dispositivo")
            # ConexãoSucesso，Automático
            client.subscribe(self.subscribe_topic)
            print(f"📥 Já：{self.subscribe_topic}")
        else:
            print(f"❌ Conexão falhou，Erro：{rc}")

    def _on_message(self, client, userdata, msg):
        """
        demensagemRecebendo。
        """
        topic = msg.topic
        content = msg.payload.decode()
        print(f"📩 paraMensagem - : {topic}，: {content}")

    def _on_publish(self, client, userdata, mid, properties=None):
        """
        demensagem。
        """
        print(f"📤 MensagemJá，Mensagem ID：{mid}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        """
        deDesconectadoConectando。
        """
        print("🔌 com MQTT DispositivodeConexãoJáDesconectado")

    def connect(self):
        """
        Conectandopara MQTT servidor。
        """
        try:
            self.client.connect(self.server, self.port, 60)
            print(f"🔗 EmConexãoparaDispositivo {self.server}:{self.port}")
        except Exception as e:
            print(f"❌ Conexão falhou，Erro: {e}")

    def start(self):
        """
        Iniciandocliente  Iniciandorede。
        """
        self.client.loop_start()

    def publish(self, message):
        """
        mensagempara。
        """
        result = self.client.publish(self.publish_topic, message)
        status = result.rc
        if status == 0:
            print(f"✅ Sucessopara `{self.publish_topic}`")
        else:
            print(f"❌ Falha，Erro：{status}")

    def stop(self):
        """
        PararredeDesconectadoConectando。
        """
        self.client.loop_stop()
        self.client.disconnect()
        print("🛑 JáPararConexão")


if __name__ == "__main__":
    pass
    # de
    # def custom_on_connect(client, userdata, flags, rc, properties=None):
    #     if rc == 0:
    #         print("🎉 ：SucessoConexãopara MQTT Dispositivo")
    #         topic_data = userdata['subscribe_topic']
    #         client.subscribe(topic_data)
    #         print(f"📥 ：Já：{topic_data}")
    #     else:
    #         print(f"❌ ：Conexão falhou，Erro：{rc}")
    #
    # def custom_on_message(client, userdata, msg):
    #     topic = msg.topic
    #     content = msg.payload.decode()
    #     print(f"📩 ：paraMensagem - : {topic}，: {content}")
    #
    # def custom_on_publish(client, userdata, mid, properties=None):
    #     print(f"📤 ：MensagemJá，Mensagem ID：{mid}")
    #
    # def custom_on_disconnect(client, userdata, rc, properties=None):
    #     print("🔌 ：com MQTT DispositivodeConexãoJáDesconectado")
    #
    # #  MqttClient ，de
    # mqtt_client = MqttClient(
    #     server="8.130.181.98",
    #     port=1883,
    #     username="admin",
    #     password="dtwin@123",
    #     subscribe_topic="sensors/temperature/request",
    #     publish_topic="sensors/temperature/device_001/state",
    #     client_id="CustomClient",
    #     on_connect=custom_on_connect,
    #     on_message=custom_on_message,
    #     on_publish=custom_on_publish,
    #     on_disconnect=custom_on_disconnect
    # )
    #
    # # Informação  paraDadospara
    # mqtt_client.client.user_data_set(
    #     {'subscribe_topic': mqtt_client.subscribe_topic}
    # )
    #
    # # Conexãopara MQTT Dispositivo
    # mqtt_client.connect()
    #
    # # Iniciando
    # mqtt_client.start()
    #
    # try:
    #     while True:
    #         # Mensagem
    #         message = input("EntradadeMensagem：")
    #         mqtt_client.publish(message)
    # except KeyboardInterrupt:
    #     print("\n⛔️ JáParar")
    # finally:
    #     # Parar  DesconectadoConexão
    #     mqtt_client.stop()
