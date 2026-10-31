"""
Datos estáticos de operadores: función del gadget y consejos.
Esto NO se lee del juego en vivo -- es información pública (extraída de las
fichas de diseño que armó el equipo, `TESIS.zip`, y completada a mano) que
se carga una sola vez como tabla de referencia para el HUD táctico nuevo y sus fichas de operador.

Cada entrada tiene:
  gadget      -- nombre corto del dispositivo/habilidad
  descripcion -- qué hace (tomado de las fichas de diseño del proyecto)
  consejo     -- un tip táctico breve que complementa la ficha del operador.

ÍCONOS: los badges en assets/ui/badges/<NombreSinTildes>.png salen de las
mismas fichas (recortados automáticamente) y se usan para el reconocimiento
por comparación de imagen en vision/operator_icon_match.py -- ver ese
módulo para cómo se usan sin tocar memoria del juego.
"""

OPERATOR_INFO = {
    "Oryx": {
        "gadget": "Embestida",
        "descripcion": "Su habilidad es un movimiento rápido que le permite atravesar paredes y derribar enemigos. Cada impacto consume salud.",
        "consejo": "Usala para sorprender desde un cuarto adyacente, pero calculá la salud que te queda después del impacto.",
    },
    "Alibi": {
        "gadget": "Hologramas Prisma",
        "descripcion": "Su dispositivo proyecta hologramas idénticos a ella. Si un atacante dispara, toca el holograma o lo atraviesa, su posición es marcada.",
        "consejo": "Colocalos en ángulos de rotación frecuente, no a la vista directa de la puerta de entrada obvia.",
    },
    "Ela": {
        "gadget": "Minas Grzmot",
        "descripcion": "Sus dispositivos adhesivos nublan la visión, limitan la movilidad y ensordecen al enemigo por varios segundos.",
        "consejo": "Colocalas cerca de rejillas o puntos de rotación rápida, no solo en la puerta principal.",
    },
    "Vigil": {
        "gadget": "Sistema ERC-7",
        "descripcion": "Su dispositivo lo invisibiliza de los drones y cámaras enemigas. Aun así, los enemigos pueden escuchar sus pasos y ruidos.",
        "consejo": "Usalo para reposicionarte sin ser redroneado, no como invisibilidad total: tus pasos te siguen delatando.",
    },
    "Lesion": {
        "gadget": "Trampas de Toxinas",
        "descripcion": "Sus trampas de toxinas, que se despliegan en el suelo, al ser pisadas infligen daño y van restando salud mientras permanezca incrustada.",
        "consejo": "Colocalas en puntos de paso obligado y fuera de la vista directa, para que se noten tarde.",
    },
    "Echo": {
        "gadget": "Dron Yokai",
        "descripcion": "Posee dos drones que se adhieren a los techos y transmiten información. También emiten ondas que aturden a los enemigos.",
        "consejo": "Usalo para aturdir justo antes de un push enemigo a tu cuarto, no solo para vigilar.",
    },
    "Mira": {
        "gadget": "Cristal Negro",
        "descripcion": "Su cristal blindado permite a los defensores ver hacia el otro lado, mientras que los atacantes solo ven un espejo opaco.",
        "consejo": "Colocalo en paredes que dan a pasillos de rotación enemiga, no a la vista directa del punto fuerte.",
    },
    "Caveira": {
        "gadget": "Silencio Letal",
        "descripcion": "Su habilidad reduce el ruido de los pasos al caminar o correr. Cuenta con un arma propia que deja a los enemigos heridos a corta distancia y permite interrogarlos.",
        "consejo": "Usala para flanquear en silencio y obtener información real del equipo rival, no solo para rematar.",
    },
    "Frost": {
        "gadget": "Trampas Garra de Oso",
        "descripcion": "Cuenta con tres trampas que, cuando un atacante las pisa, lo dejan herido en estado crítico e inmovilizado por completo a la altura de la pierna.",
        "consejo": "Escondelas en lugares donde el atacante se recuesta o se asoma (ventanas, rincones), no a simple vista.",
    },
    "Valkyrie": {
        "gadget": "Cámaras Negras",
        "descripcion": "Cuenta con tres cámaras que se pueden pegar en casi cualquier superficie y proporcionan una vista de 360 grados.",
        "consejo": "Repartilas en distintos flancos del mapa en vez de agruparlas todas cerca del punto fuerte.",
    },
    "Smoke": {
        "gadget": "Granadas de Gas Remoto",
        "descripcion": "Posee tres granadas de gas que se adhieren a cualquier superficie y se activan a distancia. La nube tóxica causa daño a cualquier operador dentro del área.",
        "consejo": "Activalas cuando ya hay atacantes adentro del área, no apenas las tirás.",
    },
    "Doc": {
        "gadget": "Pistola Estim",
        "descripcion": "Con su pistola de estimulantes puede curar a distancia a sus aliados o a él mismo y revivir a compañeros.",
        "consejo": "Guardá una carga para revivir en vez de gastarlas todas curando de a poco.",
    },
    "Jager": {
        "gadget": "Sistema de Defensa Activa ADS",
        "descripcion": "Su sistema de defensa activa destruye proyectiles entrantes y otros artefactos lanzables enemigos antes de que exploten.",
        "consejo": "Colocalo donde cubra varias ventanas/entradas a la vez, no una sola ya protegida por otro gadget.",
    },
    "Tachanka": {
        "gadget": "Lanzallamas Shumikha",
        "descripcion": "Su dispositivo dispara granadas incendiarias que rebotan en las paredes.",
        "consejo": "Usalo para negar un cuarto o pasillo completo antes de que el equipo rival lo cruce.",
    },
    "Solis": {
        "gadget": "SPEC-IO Electrosense",
        "descripcion": "Su habilidad marca dispositivos electrónicos de los oponentes.",
        "consejo": "Activala al escuchar droneo cerca para ubicar gadgets atacantes antes del push.",
    },
    "Fenrir": {
        "gadget": "F-NATT \"Dread Catcher\"",
        "descripcion": "Su dispositivo arrojadizo, que se adhiere a los muros, libera un gas que reduce de forma drástica la visión.",
        "consejo": "Usalo para cubrir una retirada o cegar un ángulo justo antes de que lo crucen.",
    },
    "Tubarao": {
        "gadget": "Capacete-Gancho",
        "descripcion": "Su dispositivo arrojadizo ralentiza a los enemigos, congela los dispositivos para detener su uso. Realza huellas si se camina por la zona congelada.",
        "consejo": "Apuntalo a dispositivos electrónicos enemigos ya colocados para inutilizarlos sin gastar munición.",
    },
    "Rook": {
        "gadget": "Armadura Rhino",
        "descripcion": "Equipado con una armadura \"Rhino\" que evita que el fuego de armas pequeñas penetre.",
        "consejo": "Agarrá la placa al empezar la fase de preparación: el beneficio dura toda la ronda.",
    },
    "Kapkan": {
        "gadget": "Trampa EDD",
        "descripcion": "Lleva una trampa cargada con explosivos que se activa por movimiento. Se coloca en marcos de puertas y ventanas.",
        "consejo": "Priorizá entradas secundarias poco vigiladas en vez de la puerta principal obvia.",
    },
    "Pulse": {
        "gadget": "Sensor Cardíaco HB-5",
        "descripcion": "Está equipado con un sensor cardíaco que puede rastrear atacantes.",
        "consejo": "Usalo apoyado contra paredes que dan a zonas de tránsito frecuente del equipo atacante.",
    },
    "Castle": {
        "gadget": "Barricadas Reforzadas TCSV",
        "descripcion": "Su habilidad única es crear barricadas reforzadas. Controla por dónde pueden avanzar los atacantes, retrasándolos.",
        "consejo": "Priorizá entradas secundarias y dejá al menos una salida de rotación para el equipo.",
    },
    "Goyo": {
        "gadget": "Escudo Volcán",
        "descripcion": "Sus escudos desplegables contienen un cartucho incendiario. Al destruirse el cartucho, el fuego se extiende por la zona y niega el paso durante varios segundos.",
        "consejo": "Colocá los escudos para bloquear una ruta de avance y coordina la detonación con el equipo; evitá encerrar a tus compañeros en la zona de fuego.",
        "escuadra": "Redhammer",
        "especialidad": "Control de área",
        "salud": 2,
        "velocidad": 2,
        "dificultad": 2,
    },
    "Azami": {
        "gadget": "Barrera Kiba",
        "descripcion": "Su dispositivo se clava en una superficie al lanzarla, se expande y después se solidifica, creando una barrera antibalas que tapa agujeros.",
        "consejo": "Usala para volver a tapar un boquete recién abierto por el equipo atacante.",
    },
    "Thorn": {
        "gadget": "Flor de Espino",
        "descripcion": "Su flor de espino, que se engancha a cualquier superficie, al detectar a un oponente expulsa hojas afiladas causando daño letal.",
        "consejo": "Colocala a media altura en puntos de paso obligado, donde no se la vea de reojo.",
    },
    "Thunderbird": {
        "gadget": "Torreta Kona",
        "descripcion": "Su torreta automática dispara dardos curativos a cualquier jugador a su alcance. También reanima compañeros cercanos.",
        "consejo": "Colocala en un punto donde cubra una zona de rotación del equipo, no un rincón aislado.",
    },
    "Melusi": {
        "gadget": "Banshee",
        "descripcion": "Si un oponente pasa cerca de su dispositivo, lo ralentiza. Solo se puede destruir con alguna herramienta o atacarlo de cerca.",
        "consejo": "Combinala con una línea de tiro propia: el enemigo queda ralentizado justo donde lo podés ver.",
    },
    "Wamai": {
        "gadget": "Mag-NET",
        "descripcion": "Su dispositivo adhesivo atrae y detona proyectiles enemigos lanzados en su radio de acción.",
        "consejo": "Colocalo en el punto por donde suelen entrar granadas o cargas, no pegado a vos.",
    },
    "Warden": {
        "gadget": "Glyph de la Verdad",
        "descripcion": "Su habilidad consiste en unas gafas inteligentes conectadas a un reloj que otorgan visión térmica a través del humo y resistencia contra efectos cegadores.",
        "consejo": "Activalas cuando el equipo atacante empiece a usar humo o flashes para despejar un cuarto.",
    },
    "Mozzie": {
        "gadget": "Pest Launcher",
        "descripcion": "Cuenta con diminutos robots que pueden usarse para marcar un dron, o desplegarse en un área para evitar acceso a un dron.",
        "consejo": "Priorizá hackear drones de reconocimiento apenas los veas, antes de que marquen tu posición.",
    },
    "Kaid": {
        "gadget": "Rtila Electroclaw",
        "descripcion": "Puede electrificar paredes reforzadas, alambre de púas, escudos desplegables y trampas o escotillas (trampillas) reforzadas.",
        "consejo": "Electrificá el gadget de un compañero (como el alambre de Jäger) para que también niegue dispositivos.",
    },
    "Clash": {
        "gadget": "Escudo CCE",
        "descripcion": "Su escudo antidisturbios indestructible electrocuta, daña y ralentiza a los enemigos. Cubre todo el frente, pero deja su espalda desprotegida.",
        "consejo": "Avanzá siempre con un compañero cubriéndote la espalda: tu escudo no protege ese lado.",
    },
    "Maestro": {
        "gadget": "Cámara Evil Eye",
        "descripcion": "Puede desplegar cámaras a prueba de balas en paredes o suelos. Estas disparan rayos láser que hacen daño y destruyen artilugios o drones.",
        "consejo": "Ubicalas en ángulos bajos o a ras del suelo, donde no se esperan cámaras normales.",
    },
    "Bandit": {
        "gadget": "Dispositivo Eléctrico Improvisado (CED)",
        "descripcion": "Es capaz de electrificar una variedad de superficies gracias a su Dispositivo Eléctrico Improvisado.",
        "consejo": "Electrificá paredes reforzadas para que los gadgets de apertura atacantes se inutilicen al tocarlas.",
    },
    "Mute": {
        "gadget": "Disruptor de Señal",
        "descripcion": "Su disruptor de señal bloquea la señal de cualquier dispositivo que esté dentro de su radio de alcance, inutilizando dispositivos enemigos.",
        "consejo": "En el marco de una barricada evita que entren drones; abajo de una pared reforzada evita cargas explosivas.",
    },
    "Solid Snake": {
        "gadget": "Codec",
        "descripcion": "Su dispositivo portátil muestra un minimapa, detecta cámaras y presencias enemigas.",
        "consejo": "Consultalo antes de rotar para evitar cámaras enemigas activas en tu camino.",
    },
    "Rauora": {
        "gadget": "Paneles Fast-Bond",
        "descripcion": "Despliega a distancia paneles antibalas en los marcos de las puertas. Tanto los atacantes como los defensores pueden accionar el panel y cambiar su estado.",
        "consejo": "Recordá que el rival también puede abrir tu panel: no confíes en él como única cobertura.",
    },
    "Striker": {
        "gadget": "Kit de doble herramienta",
        "descripcion": "Su habilidad es poder elegir dos herramientas diferentes del arsenal general de ataque.",
        "consejo": "Combiná una herramienta de apertura con una de información según lo que falte en tu equipo.",
    },
    "Deimos": {
        "gadget": "Sonda Agatha",
        "descripcion": "Su dispositivo es una sonda voladora que rastrea y marca a un defensor previamente identificado.",
        "consejo": "Usala apenas identifiques a un defensor por cámara, antes de que rote de posición.",
    },
    "Brava": {
        "gadget": "Dron Kludge",
        "descripcion": "Su habilidad es un dron de cuatro ruedas capaz de hackear los dispositivos electrónicos del equipo defensor.",
        "consejo": "Priorizá hackear cámaras y trampas antes que gadgets ya gastados.",
    },
    "Ram": {
        "gadget": "Mini Tanque ATHENA",
        "descripcion": "Su dispositivo es un mini tanque desplegable que destruye suelos, techos y paredes blandas de forma autónoma.",
        "consejo": "Mandalo por una ruta donde no haya trampas visibles antes de seguirlo con el equipo.",
    },
    "Sens": {
        "gadget": "Proyector R.O.U. Ghostwheel",
        "descripcion": "Posee un proyector en forma de rueda. A medida que rueda, despliegan una cortina de luz que corta las líneas de visión enemigas.",
        "consejo": "Usalo para cruzar una zona abierta cubierta por una cámara o ángulo defensivo fuerte.",
    },
    "Osa": {
        "gadget": "Escudo Talon-8",
        "descripcion": "Lleva un escudo transparente el cual puede llevar en las manos como cobertura o desplegar en marcos de puertas, ventanas y en el suelo.",
        "consejo": "Desplegalo en el marco por donde vas a entrar, no solo lo lleves en mano.",
    },
    "Flores": {
        "gadget": "Dron RCE-Ratero",
        "descripcion": "Su dron explosivo controlado a distancia puede destruir la utilidad defensiva, abrir superficies blandas e infligir daño a enemigos cercanos.",
        "consejo": "Mandalo primero a destruir trampas visibles antes de que el equipo avance.",
    },
    "Zero": {
        "gadget": "Lanzador Argus",
        "descripcion": "Su lanzador dispara cuatro cámaras que se adhieren a superficies. Ofrecen visión de ambos lados y es capaz de disparar un láser.",
        "consejo": "Repartilas en distintos cuartos para cubrir más información, no todas apuntando al mismo lugar.",
    },
    "Ace": {
        "gadget": "Cargas S.E.L.M.A.",
        "descripcion": "Sus tres dispositivos lanzables utilizan presión hidráulica para destruir superficies destructibles y reforzadas.",
        "consejo": "Abrí una ruta de rotación nueva además del boquete obvio hacia el objetivo.",
    },
    "Iana": {
        "gadget": "Holograma Gemini",
        "descripcion": "Su habilidad es un holograma remoto que imita sus movimientos y sonidos para engañar y obtener información.",
        "consejo": "Usalo para asomarte a un ángulo peligroso sin exponerte vos.",
    },
    "Kali": {
        "gadget": "Lanza LV Explosiva (CSRX 300)",
        "descripcion": "Su lanza explosiva destruye dispositivos electrónicos enemigos. También perfora superficies, explotando por ambos lados del muro o barricada.",
        "consejo": "Apuntá primero a gadgets defensivos clave (cámaras, trampas) antes que a paredes.",
    },
    "Amaru": {
        "gadget": "Gancho Garra-Afuera",
        "descripcion": "Su gancho le permite impulsarse rápidamente hacia ventanas, balcones, cornisas y escotillas abiertas.",
        "consejo": "Usalo para entradas rápidas por lugares que el equipo defensor no espera cubrir.",
    },
    "Nokk": {
        "gadget": "Reductor de Presencia HEL",
        "descripcion": "Su dispositivo \"Reductor de presencia\" lo invisibiliza ante cámaras enemigas.",
        "consejo": "Combinalo con pasos agachados: seguís siendo audible, no invisible al oído.",
    },
    "Gridlock": {
        "gadget": "Trax Agüijón",
        "descripcion": "Sus tres dispositivos portátiles, al lanzarlos, despliegan una red de alfombrillas con púas metálicas que cubren una gran superficie.",
        "consejo": "Usalas para asegurar una ruta de rotación detrás del equipo, no solo al entrar.",
    },
    "Nomad": {
        "gadget": "Minas Airjab",
        "descripcion": "Posee tres minas adhesivas que, al acercarse un enemigo, la mina explota y lo hace volar por los aires, desorientándolo.",
        "consejo": "Colocalas en rutas de rotación típicas del defensor, no solo en la entrada principal.",
    },
    "Maverick": {
        "gadget": "Soplete Breacher",
        "descripcion": "Su dispositivo es un soplete exotérmico silencioso que puede cortar cualquier superficie, incluso las paredes reforzadas.",
        "consejo": "Abrí una mirilla pequeña primero para ver adentro antes de abrir un boquete grande.",
    },
    "Lion": {
        "gadget": "Dron EE-ONE-D",
        "descripcion": "Su dispositivo es un dron que escanea el mapa en busca de enemigos. Si, mientras escanea, un enemigo se mueve, queda marcado.",
        "consejo": "Avisale al equipo que vas a escanear para que todos queden quietos y no delaten su propia posición.",
    },
    "Finka": {
        "gadget": "Adrenalina Rápida",
        "descripcion": "Su dispositivo da vida extra a Finka y a todos sus compañeros sin importar en qué parte del mapa estén. También puede revivirlos.",
        "consejo": "Guardala para el momento del push final, no la gastes apenas arranca la ronda.",
    },
    "Dokkaebi": {
        "gadget": "Hackeo Lógico",
        "descripcion": "Su habilidad consiste en hackear y alterar los dispositivos móviles del enemigo haciéndolos sonar y así revelando su posición.",
        "consejo": "Usala después de una baja para reactivar cámaras del defensor caído.",
    },
    "Zofia": {
        "gadget": "Lanzagranadas KS79 Lifeline",
        "descripcion": "Su lanzagranadas de dos tipos de munición explotan contra una superficie o emiten un fogonazo y un sonido que revela la posición enemiga cercana.",
        "consejo": "Usá la concusión para despejar un cuarto antes de entrar, no solo para causar daño.",
    },
    "Ying": {
        "gadget": "Cargas Candela",
        "descripcion": "Su dispositivo es un conjunto de cargas aturdidoras que se pueden lanzar o adherir a superficies para activarse del otro lado, aturdiendo al enemigo.",
        "consejo": "Pegalas en paredes que dan al cuarto objetivo para aturdir sin exponerte en la puerta.",
    },
    "Jackal": {
        "gadget": "Gafas Eyenox",
        "descripcion": "Sus gafas de rastreo le permiten ver y escanear las huellas de los defensores en el suelo.",
        "consejo": "Escaneá antes de que el defensor rote de posición: la huella más fresca es la más útil.",
    },
    "Hibana": {
        "gadget": "Lanzador X-KAIROS",
        "descripcion": "Su lanzador dispara proyectiles explosivos que pueden detonarse a distancia, abriendo brechas en superficies blandas o reforzadas.",
        "consejo": "Abrí varias mirillas pequeñas en vez de gastar todo en un solo boquete grande.",
    },
    "Capitao": {
        "gadget": "Ballesta Tactical Crossbow",
        "descripcion": "Su ballesta con dos tipos de munición: pernos que queman el oxígeno y dañan, y por otro lado, microbots de humo que bloquean la visión rival.",
        "consejo": "Usá el humo para cortar una línea de tiro defensiva antes de cruzar un pasillo expuesto.",
    },
    "Blackbeard": {
        "gadget": "Escudo de Mira Óptica",
        "descripcion": "Su escudo se ajusta en forma al estar de pie o agachado, permite desplegar un cristal para disparar de frente y puede destruir paredes ligeras y barricadas.",
        "consejo": "Usalo para asomarte a duelos de larga distancia sin exponer el cuerpo completo.",
    },
    "Buck": {
        "gadget": "Escopeta Skeleton Key",
        "descripcion": "Además de su escopeta, que puede abrir agujeros en paredes, puede alternar de manera instantánea entre el fusil y la escopeta.",
        "consejo": "Abrí una mirilla a la altura de los pies para ver gadgets en el piso antes de entrar.",
    },
    "Sledge": {
        "gadget": "Martillo Caber-19",
        "descripcion": "Su dispositivo es un martillo de demolición que le permite romper superficies blandas y obstáculos de forma rápida y silenciosa.",
        "consejo": "Abrí líneas de tiro nuevas por superficies blandas en vez de pasar siempre por la puerta.",
    },
    "Ash": {
        "gadget": "Lanzador M120 CREM",
        "descripcion": "Su lanzador dispara dos proyectiles explosivos capaces de adherirse a superficies y detonar tras un breve retardo.",
        "consejo": "Usalo para abrir y despejar un cuarto a la vez en una sola jugada rápida.",
    },
    "Thermite": {
        "gadget": "Carga Exotérmica",
        "descripcion": "Su habilidad son dos cargas exotérmicas que le permiten destruir paredes, suelos y trampillas reforzadas.",
        "consejo": "Pedí cobertura antes de plantarla: el momento de la apertura es el más vulnerable.",
    },
    "Twitch": {
        "gadget": "Dron Shock",
        "descripcion": "Cuenta con dos drones que disparan rayos láser capaces de destruir o desactivar dispositivos electrónicos enemigos.",
        "consejo": "Priorizá destruir cámaras y trampas antes de que el equipo empiece a avanzar.",
    },
    "Blitz": {
        "gadget": "Escudo G52-Tactical",
        "descripcion": "Posee un escudo equipado con un dispositivo con cinco cargas de un destello integrado que le permite cegar a los enemigos.",
        "consejo": "Avanzá con un compañero cubriéndote, el destello te deja momentáneamente expuesto también a vos.",
    },
    "Glaz": {
        "gadget": "Mira Flip Sight PSS9",
        "descripcion": "Su dispositivo es una mira plegable con un visor térmico que resalta a los enemigos a través del humo o zonas de baja visibilidad.",
        "consejo": "Combinalo con humo propio para pelear a través de él con ventaja.",
    },
    "Thatcher": {
        "gadget": "Granadas EMP",
        "descripcion": "Su dispositivo son granadas que desactivan temporalmente cualquier dispositivo electrónico enemigo.",
        "consejo": "Usalas justo antes de que el equipo abra una pared electrificada o trampas.",
    },
    "Montagne": {
        "gadget": "Escudo Extensible",
        "descripcion": "Su escudo lo protege totalmente contra balas y explosivos. Mientras el escudo está abierto, no puede usar armas.",
        "consejo": "Usalo para scoutear información y absorber disparos, no para buscar bajas vos mismo.",
    },
    "IQ": {
        "gadget": "Detector Electrosense",
        "descripcion": "Su dispositivo le permite localizar aparatos electrónicos enemigos y aliados a través de paredes, pisos y obstáculos.",
        "consejo": "Revisá el detector antes de abrir una pared para ubicar trampas electrónicas del otro lado.",
    },
    "Fuze": {
        "gadget": "Lanzagranadas Cluster Charge",
        "descripcion": "Su habilidad le permite disparar cinco subgranadas explosivas en forma de abanico a través de superficies.",
        "consejo": "Usalo contra cuartos con varios defensores agrupados, no contra uno vacío.",
    },
    "Skopos": {
        "gadget": "Robots gemelos Skopós",
        "descripcion": "Su habilidad le permite controlar a distancia dos robots gemelos en lugar de aparecer físicamente en el mapa.",
        "consejo": "Usá uno para scoutear mientras el otro queda de respaldo en una posición segura.",
    },
    "Aruni": {
        "gadget": "Matriz Láser Surya Gate",
        "descripcion": "Su dispositivo proyecta una matriz láser que detecta a cualquiera que la atraviese. Al identificar a un intruso, causa daño.",
        "consejo": "Colocala en pasillos de rotación largos, lejos de donde el equipo defensor pasa seguido.",
    },
    "Denari": {
        "gadget": "Red ARB/N \"Loas\"",
        "descripcion": "Puede conectar hasta siete dispositivos; al pisarlo, ralentiza y daña a los enemigos. Más dispositivos conectados crean una red de láseres bloqueando un área.",
        "consejo": "Conectá varios para cubrir un pasillo entero en vez de un solo punto aislado.",
    },
    "Grim": {
        "gadget": "Colmenas Fast-Ball",
        "descripcion": "Dispara colmenas que se adhieren a superficies. Al activarse, liberan microdrones que detectan a cualquier defensor que esté en la zona.",
        "consejo": "Lanzalas hacia el objetivo antes de entrar, para saber si hay defensores esperando.",
    },
    "Noor": {
        "gadget": "Disparalanzas",
        "descripcion": "Su habilidad es un disparalanzas que dispara 5 proyectiles que perforan escudos y superficies destructibles.",
        "consejo": "Usalo contra operadores con escudo que estén bloqueando una línea de tiro clave.",
    },
    "Sentry": {
        "gadget": "Kit de doble gadget",
        "descripcion": "Posee un kit de gadgets que le permite elegir dos dispositivos secundarios diferentes de cualquier otro defensor.",
        "consejo": "Elegí una combinación que cubra lo que le falta al resto del equipo defensor.",
    },
}


def get_operator_info(name: str) -> dict | None:
    return OPERATOR_INFO.get(name)


WALL_REINFORCEMENT_INFO = {
    "descripcion": (
        "Refuerza una pared destructible, haciéndola resistente a explosivos "
        "y disparos (excepto herramientas específicas como el mazo)."
    ),
    "consejo": "Priorizá reforzar paredes que dan a ángulos de rotación enemiga, no todas las paredes del cuarto.",
}

# Lista completa de operadores para que vision/team_ocr.py y
# vision/operator_icon_match.py puedan reconocer cualquier nombre/ícono
# leído en pantalla, aunque algunos todavía no tengan ficha completa
# arriba (ej. Goyo, que no vino en las fichas de diseño del proyecto pero
# sí es un operador real). Si Ubisoft agrega operadores nuevos y no están
# acá, el reconocimiento simplemente no los va a detectar -- no rompe nada.
ALL_OPERATORS = sorted(set(list(OPERATOR_INFO.keys()) + [
    "Goyo", "Striker",
]))
