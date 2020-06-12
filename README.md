# Kamailio Playground

## Funcionamiento de la configuración de Kamailio

Kamailio utiliza un lenguajde de scripting para su configuración, usualmente encontrado en la ubicación `/etc/kamailio/kamailio.cfg`. Este lenguaje de scripting llamado `native scripting` fue desarrollado específicamente para Kamailio entre 2001-2002.

La configuración esta compuesta por las siguientes secciones:

1. **Global Parameters**: Parámetros de configuración global.
2. **Loading Modules**: Carga de módulos a utilizar.
3. **Module Parameters**: Configuración de módulos a través de parámetros.
4. **Routing Blocks**: Bloques de configuración para gestionar los mensajes y las respuestas.

Esta configuración es leída solo una vez al momento que se inicia el proceso de Kamailio. Luego se compila, y se almacena en memoria. Una vez cargada, cada mensaje o respuesta recibida será tratado en base a esta configuración.

## Kamailio Proxy en Modo Bridge

En este escenario, se configura el kamailio en un servidor con dos interfaces de red. Una que mira hacia una DMZ (10.0.1.0/24), y otra que mira hacia la red interna (10.0.2.0/24). La interfaz del Kamailio esta públicada en Internet con la IP 1.1.1.1. 

![Kamailio en modo bridge](images/kamailio_bridge_mode.png)

Toda la gestión de las sesiones es manejada por la PBX, el Kamailio solamente oficia de Proxy. La configuración mínima para correr el Kamailio en esta configuración es la siguiente:

```kamailio
####### Global Parameters #########
# Listen LAN
listen = tcp:10.0.2.100:5060

# Listen WAN
listen = tcp:10.0.1.100:5060
listen = udp:10.0.1.100:5060

# TCP
disable_tcp = no
tcp_async = yes
tcp_children = 2

# Alias
#alias="kamailio.example.com:5060"

####### Module Load   ########
loadmodule "tm.so"
loadmodule "tmx.so"
loadmodule "rr.so"
loadmodule "pv.so"
loadmodule "textops.so"
loadmodule "xlog.so"

loadmodule "rtpproxy.so"

####### Module Configuration #######
modparam("rtpproxy", "rtpproxy_sock", "udp:127.0.0.1:7722")

####### Routing Logic ########

/* Main SIP request routing logic
 * - processing of any incoming SIP request starts with this route
 * - note: this is the same as route { ... } */
request_route {
	rtpproxy_manage('iewc');

  t_relay("10.0.2.200", "5060");
}

onreply_route{
	if (has_body("application/sdp")) {
		rtpproxy_manage("iewc");
	}
}
```

Básicamente, el Kamailio reenvía todos los mensajes que recibe a la PBX. Y luego, utiliza el módulo `rtpproxy` para gestionar el audio entre participantes.

Es importante mencionar que con esta conversación solo se esta manejando el caso de que los mensajes salga de un interno y vayan hacia la PSTN. Además, no funciona la llamada en espera ni la pausa. Para que esto funcione, es necesario agregar más detalles a la configuración.

### `rtpproxy`

Para que el módulo `rtpproxy` funcione, es necesario contar con un proceso de `rtpproxy` corriendo en algún servidor. En este ejemplo, el proceso se ejecuta en la misma maquina.

`rtpproxy` puede ser ejecutado en modo bridge, para esto, se puede correr el proceso con las siguientes opciones:

```bash
rtpproxy \
  -A 1.1.1.1/10.0.2.100 \
  -u rtpproxy rtpproxy \
  -l 10.0.1.100/10.0.2.100 \
  -m 10000 -M 20000 \
  -s udp:*:7722 \
  -d INFO
```

- `-A`: Indica las IP sobre las cuales esta públicado el servidor. Esta opción es útil para configurar interfaces públicadas en Internet. Cuando se colocan dos IPs separadas por una barra (`/`) indica que el `rtpproxy` debe trabajar en modo bridge.
- `-u`: Indica el usuario que se debe utilizar para correr el proceso.
- `-l`: Indica las IP sobre las cuales debe escuchar el `rtpproxy`. Cuando se colocan dos IPs separadas por una barra (`/`) indica que el `rtpproxy` debe trabajar en modo bridge.
- `-m`: Indica el rango inferior de puertos que debe utilizar el `rtproxy`.
- `-M`: Indica el rango superior de puertos que debe utilizar el `rtpproxy`.
- `-s`: Indica el socket en el que el `rtpproxy` escucha comandos de control.
- `-d`: Indica el modo de logs. En este caso `INFO`.

El Kamailio se comunicara con el proceso de `rtpproxy` a través del socket configurado con `-s`. Esta configuración se realiza modificando la variable `rtpproxy_sock` del módulo `rtpproxy`.

```kamailio
modparam("rtpproxy", "rtpproxy_sock", "udp:127.0.0.1:7722")
```

Dentro del módulo `rtpproxy` existe una función llamada `rtpproxy_manage` que se encarga de gestionar la interacción con el proceso de `rtpproxy`. Esta función, consume una serie de flags que modifican su comportamiento. En este caso:

```kamailio
rtpproxy_manage("iew");
```

> i, e - these flags specify the direction of the SIP message. These flags only make sense when rtpproxy is running in bridge mode. 'i' means internal network (LAN), 'e' means external network (WAN). 'i' corresponds to rtpproxy's first interface, 'e' corresponds to rtpproxy's second interface. You always have to specify two flags to define the incoming network and the outgoing network. For example, 'ie' should be used for SIP message received from the local interface and sent out on the external interface, and 'ei' vice versa. Other options are 'ii' and 'ee'. So, for example if a SIP requests is processed with 'ie' flags, the corresponding response must be processed with 'ie' flags.
> 
> c - flags to change the session-level SDP connection (c=) IP if media-description also includes connection information.
> 
>w - flags that for the UA from which message is received, support symmetric RTP must be forced.
>
> **[Documentación de `rtpproxy`](https://kamailio.org/docs/modules/5.3.x/modules/rtpproxy.html)**

- `ie`: Indica la dirección de los mensajes SIP cuando `rtpproxy` opera en modo bridge. `i` indica la red interna, y e indica la red externa. Siempre es necesario indicar los dos flags, lo que puede modificarse es el órden de los flags. Las combincaciones posibles on `ii`, `ee`, `ie`, e `ei`. `ie` indica que el mensaje es recibido por la interface local, y es enviado por la externa. Los mensajes procesado con un par de flags, deben ser procesados en la respuesta con el mismo par de flags.
- `c`: Indica que los campos `c=` del cuerpo SDP del mensaje SIP también deben ser modificados.
- `w`: Indica que se debe forzar el uso de RTP simetrico para el UA que envía el mensaje.

## Python KEMI Interpreter

Con el fín de exponer lenguajes de scripting más completos que el nativo de Kamailio, se creo el KEMI Interprete. El mismo, permite la carga de ciertos módulos, que permiten escribir la configuración de Kamailio en otros lenguajes de scripting como Python, Lua, Ruby, JavaScript, etc.

Correr la configuración de Kamailio con esta configuración tiene varias ventajas:

1. Se puede hacer uso de las librerías disponibles para cada lenguaje de scripting.
2. Es posible reemplazar la configuración del Kamailio en caliente, sin necesidad de reiniciar el proceso.
3. La posibilidad de utilizar un lenguaje de scripting más completo.

Para utilizar el módulo de Python, es necesario cargar el módulo `app_python3`.

```kamailio
####### Module Load   ########
loadmodule "app_python3.so"

####### Module Configuration #######
modparam("app_python3", "<script_name>", "<path_to_script>)

####### Routing Logic ########
cfgengine "python"
```

Dentro del script the Python se debe declarar la función global `mod_init()`. Esta función instanciara un nuevo objeto que implementará los métodos necesarios para que Kamailio ejecute.

Metodos relevantes:

- `ksr_request_route(self, msg)`: Ejecutada cada vez que se recibe un mensaje SIP. Equivalente a `request_route`.
- `ksr_reply_route(self, msg)`: Ejecutada cada vez que se recibe una respuesta de un mensaje SIP. Equivalente a `reply_route`.
- `ksr_onsend_route(self, msg)`: Ejecutada cada vez que se va a enviar un mensaje, y opcionalmente, cada vez que se quiera enviar una respuesta. Equivalente a `onsend_route`.
- `branch route callback`: Metodo a ejecutar cuando se pasa como argumento a la función `KSR.tm.t_on_branch()`.
- `onreply route callback`: Metodo a ejecutar cuando se pasa como argumento a la función `KSR.tm.t_on_reply()`.
- `failure route callback`: Metodo a ejecutar cuando se pasa como argumento a la función `KSR.tm.t_on_failure`.
- `branch failure route callback`: Metodo a ejecutar cuando se pasa como argumento a la función `KSR.tm.t_on_branch_failure`.

Esta es una configuración base para ejecutar Python como lenguaje de scripting en Kamailio:

```kamailio
####### Global Parameters #########
# Listen LAN
listen = tcp:10.0.2.100:5060

# Listen WAN
listen = tcp:10.0.1.100:5060
listen = udp:10.0.1.100:5060

# TCP
disable_tcp = no
tcp_async = yes
tcp_children = 2

# Alias
#alias="kamailio.example.com:5060"

####### Module Load   ########
loadmodule "tm.so"
loadmodule "tmx.so"
loadmodule "rr.so"
loadmodule "pv.so"
loadmodule "textops.so"
loadmodule "xlog.so"

loadmodule "app_python3.so"

####### Module Configuration #######
modparam("app_python3", "load", "/usr/local/kamailio/kamailio.py")
cfengine "python"
```

```python
import KSR as KSR

def ksr_info(message):
  KSR.info(f"====== {message} \n")

# Global function to instantiate kamailio class object.
# It is executed when Kamailio app_python module is initialized.
def mod_init():
  ksr_info('From python mod init")
  return Kamailio()


# Kamailio class containing the entire configuration
class Kamailio:
    def __init__(self):
        ksr_info('Kamailio.__init__")
    
    # SIP request routing
    def ksr_request_route(self, msg):
        ksr_info('Kamailio.ksr_request_route')
```



