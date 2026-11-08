"""Contenido de la web: servicios, proceso de trabajo y artículos del blog."""

SERVICES = [
    {
        "slug": "auditoria-interna",
        "nombre": "Auditoría interna de seguridad",
        "ref": "ISO 19011",
        "resumen": "Revisamos con criterio independiente cómo se aplican de verdad tus políticas y controles, antes de que lo haga una auditoría externa o un regulador.",
        "para_quien": "Organizaciones que ya tienen un sistema de gestión, o lo están montando, y quieren saber dónde están antes de certificarse.",
        "entregable": "Informe con hallazgos clasificados (no conformidades, observaciones y oportunidades de mejora) y un plan de acción priorizado.",
    },
    {
        "slug": "iso-27001",
        "nombre": "Implantación y auditoría ISO/IEC 27001",
        "ref": "ISO/IEC 27001:2022",
        "resumen": "Te acompañamos desde el alcance hasta la certificación: análisis de riesgos, declaración de aplicabilidad, políticas y preparación de la auditoría externa.",
        "para_quien": "Empresas que quieren demostrar a clientes y licitaciones que gestionan la seguridad de la información con un método reconocido.",
        "entregable": "Sistema de gestión documentado, declaración de aplicabilidad y auditoría interna previa a la certificación.",
    },
    {
        "slug": "ens",
        "nombre": "Adecuación al Esquema Nacional de Seguridad",
        "ref": "Real Decreto 311/2022",
        "resumen": "Categorizamos tus sistemas, aplicamos las medidas del Anexo II que corresponden y preparamos la auditoría de conformidad.",
        "para_quien": "Administraciones públicas y empresas que prestan servicios al sector público.",
        "entregable": "Categorización de sistemas, declaración de aplicabilidad, plan de adecuación e informe de preparación para la auditoría.",
    },
    {
        "slug": "nis2",
        "nombre": "Adecuación a NIS y NIS2",
        "ref": "Directiva (UE) 2022/2555",
        "resumen": "Analizamos si te afecta la normativa, medimos la distancia frente a las medidas de gestión de riesgos exigidas y definimos cómo notificar incidentes.",
        "para_quien": "Entidades de sectores esenciales e importantes, y proveedores que trabajan para ellas.",
        "entregable": "Análisis de aplicabilidad, informe de brechas, procedimiento de notificación de incidentes y propuesta de gobernanza.",
    },
    {
        "slug": "iso-42001",
        "nombre": "Gestión de la inteligencia artificial",
        "ref": "ISO/IEC 42001",
        "resumen": "Ordenamos cómo tu organización desarrolla o usa sistemas de IA: inventario, riesgos, responsabilidades y controles.",
        "para_quien": "Organizaciones que ya usan IA en sus procesos o en sus productos y necesitan gobernarla.",
        "entregable": "Inventario de sistemas de IA, evaluación de riesgos, políticas y preparación para la certificación.",
    },
    {
        "slug": "rgpd",
        "nombre": "Protección de datos personales",
        "ref": "RGPD y LOPDGDD",
        "resumen": "Revisamos el tratamiento de datos personales y dejamos al día la documentación que exige la normativa.",
        "para_quien": "Cualquier organización que trate datos de clientes, empleados o usuarios.",
        "entregable": "Registro de actividades de tratamiento, evaluaciones de impacto cuando proceda y protocolo ante brechas de datos.",
    },
    {
        "slug": "pentesting",
        "nombre": "Análisis de vulnerabilidades y pruebas de intrusión",
        "ref": "Alcance y autorización por escrito",
        "resumen": "Probamos tus sistemas como lo haría un atacante, pero con un alcance pactado y autorización escrita previa.",
        "para_quien": "Equipos que quieren comprobar la seguridad real de una aplicación web, una red o una infraestructura.",
        "entregable": "Informe ejecutivo y técnico con evidencias, nivel de riesgo de cada hallazgo y recomendaciones de corrección.",
    },
    {
        "slug": "riesgos-continuidad",
        "nombre": "Análisis de riesgos y continuidad de negocio",
        "ref": "MAGERIT e ISO 22301",
        "resumen": "Identificamos qué activos importan, qué les puede pasar y cómo seguir funcionando si ocurre.",
        "para_quien": "Organizaciones que dependen de sus sistemas para operar y no pueden permitirse paradas largas.",
        "entregable": "Mapa de riesgos, análisis de impacto en el negocio y plan de continuidad.",
    },
    {
        "slug": "formacion-phishing",
        "nombre": "Formación y simulacros de phishing",
        "ref": "Concienciación",
        "resumen": "Sesiones cortas y prácticas para el personal, y campañas de phishing simulado con permiso de la dirección.",
        "para_quien": "Plantillas de cualquier tamaño: la mayoría de incidentes empieza con un correo o una contraseña débil.",
        "entregable": "Sesiones de formación, resultados de la campaña y recomendaciones por departamento.",
    },
    {
        "slug": "ciso-externo",
        "nombre": "Responsable de seguridad externo",
        "ref": "CISO as a service",
        "resumen": "Asumimos la función de responsable de seguridad a tiempo parcial: seguimiento del plan, comités e incidentes.",
        "para_quien": "Organizaciones que necesitan esa figura, por ejemplo para el ENS o ISO 27001, pero no tienen un perfil interno.",
        "entregable": "Plan anual de seguridad, informes periódicos a la dirección y atención ante incidentes.",
    },
]

PROCESS = [
    ("Diagnóstico inicial", "Una reunión para entender tu actividad, tus sistemas y qué normativa te afecta."),
    ("Análisis de brechas", "Comparamos lo que haces hoy con lo que exige la norma y listamos las diferencias."),
    ("Plan de acción", "Ordenamos las correcciones por riesgo y esfuerzo, con responsables y plazos realistas."),
    ("Auditoría y seguimiento", "Verificamos que los cambios funcionan y repetimos la revisión cuando haga falta."),
]

POSTS = [
    {
        "slug": "ens-iso-27001-nis2",
        "titulo": "ENS, ISO 27001 y NIS2: en qué se parecen y en qué no",
        "fecha": "2026-10-14",
        "resumen": "Tres marcos que se mencionan juntos, pero que no obligan ni se certifican igual.",
        "cuerpo": [
            "El Esquema Nacional de Seguridad (ENS) es una norma española de obligado cumplimiento para el sector público y para las empresas que le prestan servicios. Define medidas concretas, organizadas por categoría del sistema.",
            "ISO/IEC 27001 es un estándar internacional voluntario. No dice qué medidas aplicar de forma fija: te pide gestionar los riesgos y justificar los controles que eliges. Se puede certificar con una entidad acreditada.",
            "NIS2 es una directiva europea que obliga a determinadas entidades de sectores esenciales e importantes a gestionar sus riesgos de ciberseguridad y a notificar incidentes. Sustituye a la directiva NIS original.",
            "Los tres comparten la misma base: conocer tus activos, gestionar riesgos, controlar accesos, tener copias de seguridad, responder a incidentes y mejorar de forma continua. Por eso un buen trabajo en uno suele facilitar los otros.",
        ],
    },
    {
        "slug": "auditoria-interna-primero",
        "titulo": "Por qué conviene hacer una auditoría interna antes de la externa",
        "fecha": "2026-09-30",
        "resumen": "Encontrar tus propios fallos con tiempo es más barato que descubrirlos delante del certificador.",
        "cuerpo": [
            "Una auditoría interna es una revisión que hace la propia organización, o un tercero que trabaja para ella, para comprobar si lo que está escrito se cumple en la práctica.",
            "Su ventaja es el momento: los hallazgos aparecen antes de la auditoría de certificación, cuando todavía se pueden corregir sin presión ni consecuencias sobre el certificado.",
            "Una buena auditoría interna no busca culpables. Clasifica lo encontrado (no conformidades, observaciones y mejoras), asigna responsables y fija plazos de corrección.",
            "Además, la mayoría de normas la exigen: tanto ISO 27001 como el ENS esperan que revises periódicamente tu propio sistema.",
        ],
    },
    {
        "slug": "cinco-comprobaciones",
        "titulo": "Cinco comprobaciones de seguridad que puedes hacer esta semana",
        "fecha": "2026-09-12",
        "resumen": "Medidas básicas que cualquier pyme puede revisar sin gran presupuesto.",
        "cuerpo": [
            "Doble factor de autenticación: actívalo al menos en correo, acceso remoto y paneles de administración.",
            "Copias de seguridad: no basta con hacerlas. Prueba a restaurar una y comprueba cuánto tardas y si los datos están completos.",
            "Inventario: apunta qué equipos, aplicaciones y servicios en la nube usa tu organización. Lo que no se conoce no se protege.",
            "Actualizaciones: revisa qué sistemas llevan meses sin actualizarse, sobre todo los que están expuestos a internet.",
            "Personas: una sesión corta sobre correos sospechosos y contraseñas reduce más riesgo del que parece.",
        ],
    },
]


def get_service(slug):
    return next((s for s in SERVICES if s["slug"] == slug), None)


def get_post(slug):
    return next((p for p in POSTS if p["slug"] == slug), None)

CREDENCIALES = [
    {
        "titulo": "Objetivo: ISO/IEC 27001 en 2027",
        "texto": "Queremos certificar nuestro propio sistema de gestión de seguridad de la información con un organismo acreditado, para demostrar que aplicamos lo que recomendamos.",
    },
    {
        "titulo": "Método: ISO 19011",
        "texto": "Nuestras auditorías internas siguen las directrices de la ISO 19011 para planificar, ejecutar e informar.",
    },
    {
        "titulo": "Marcos de referencia",
        "texto": "ISO/IEC 27001, Esquema Nacional de Seguridad, NIS2, ISO/IEC 42001 y RGPD: los textos oficiales son nuestra referencia de trabajo.",
    },
]

VALORES = [
    ("Lenguaje claro", "Cada hallazgo se explica sin jerga, con su riesgo y una recomendación concreta."),
    ("Alcance por escrito", "Acordamos por escrito qué se revisa, cuándo y con qué medios antes de empezar."),
    ("Autorización previa", "Ninguna prueba técnica se hace sin autorización escrita de la dirección."),
    ("Confidencialidad", "La información de tu organización solo la ve el equipo que trabaja en tu caso."),
]
