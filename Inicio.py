import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="ESTRA - Análisis Energético",
    page_icon="🏭",
    layout="wide"
)

# Título principal
st.title("ESTRA - Plataforma inteligente de Analítica de eficiencia energética y productiva")

# Función para generar datos sintéticos
def generar_datos_energia(centro, periodo="Semana", numero_periodos=24):
    """Genera datos sintéticos para cada centro de costos según el periodo seleccionado"""
    tiempo = np.arange(1, numero_periodos + 1)
    
    # Parámetros base para cada máquina
    parametros = {
        "H75": {
            "base": 180,
            "amplitud1": 35,
            "amplitud2": 25,
            "fase1": 0,
            "fase2": np.pi
        },
        "Extrusora LEISTRITZ ZSE-27": {
            "base": 220,
            "amplitud1": 50,
            "amplitud2": 40,
            "fase1": np.pi/4,
            "fase2": -np.pi/4
        },
        "Inyectora ENGEL e-motion 310": {
            "base": 160,
            "amplitud1": 30,
            "amplitud2": 20,
            "fase1": np.pi/2,
            "fase2": -np.pi/2
        }
    }
    
    params = parametros[centro]
    
    # Ajustar valores base según el periodo
    factor_periodo = {
        "Día": 1/7,      # Factor diario (1/7 de la semana)
        "Semana": 1,     # Factor base
        "Mes": 4.33      # Factor mensual (aprox 4.33 semanas por mes)
    }
    
    factor = factor_periodo.get(periodo, 1)
    base_ajustada = params["base"] * factor
    amp1_ajustada = params["amplitud1"] * factor
    amp2_ajustada = params["amplitud2"] * factor
    
    # Generar curvas simétricas
    frente_a_abt = base_ajustada + amp1_ajustada * np.sin(2 * np.pi * tiempo / numero_periodos + params["fase1"])
    frente_a_linea_base = base_ajustada - amp2_ajustada * np.sin(2 * np.pi * tiempo / numero_periodos + params["fase2"])
    
    # Asegurar que empiecen y terminen en el mismo punto
    frente_a_abt[0] = frente_a_abt[-1] = base_ajustada
    frente_a_linea_base[0] = frente_a_linea_base[-1] = base_ajustada
    
    return tiempo, frente_a_abt, frente_a_linea_base

# Función para mostrar estadísticas
def mostrar_estadisticas(centro_seleccionado, periodo_seleccionado):
    """Muestra estadísticas del centro seleccionado"""
    numero_periodos = {
        "Día": 30,      # 30 días
        "Semana": 24,   # 24 semanas
        "Mes": 12       # 12 meses
    }
    
    tiempo, frente_a_abt, frente_a_linea_base = generar_datos_energia(
        centro_seleccionado, 
        periodo_seleccionado, 
        numero_periodos[periodo_seleccionado]
    )
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        CPCL=35
        delta_cpcl=2
        st.metric(
            label="CUSUM  PCL",
            value=f"+{CPCL:.0f} M",
            delta=f"±{delta_cpcl:.1f}"
        )
    
    with col2:
        CABT=25
        st.metric(
            label="CUSUM ABT", 
            value=f"-{CABT:.1f} M",
        )
    
    with col3:
        COeq=75
        st.metric(
            label="C02 Eq.",
            value=f"{COeq:.1f} Ton",
        )
    
    with col4:
        Tendencia="Desc."
        delta_ten=-4
        st.metric(
            label="Tendencia",
            value=f"{Tendencia} ",
            delta=f"{(delta_ten):.1f}%"
        )
        
    with col5:
        Resultado="Mejora"
        st.metric(
            label="Resultado",
            value=f"{Resultado} "
        )       

# Sidebar para controles
st.sidebar.header("🔧 Panel de Control")

# Selectbox para máquinas
maquinas = [
    "H75",
    "Extrusora LEISTRITZ ZSE-27", 
    "Inyectora ENGEL e-motion 310"
]

maquina_seleccionada = st.sidebar.selectbox(
    "Selecciona el centro de costos de energía:",
    maquinas,
    index=0
)

# Selectbox para periodo de consulta
st.sidebar.markdown("---")
periodo_seleccionado = st.sidebar.selectbox(
    "📅 Selecciona el periodo de consulta:",
    ["Día", "Semana", "Mes"],
    index=1  # Por defecto "Semana"
)

# Información adicional del periodo
info_periodo = {
    "Día": "📊 Análisis diario (últimos 30 días)",
    "Semana": "📊 Análisis semanal (últimas 24 semanas)", 
    "Mes": "📊 Análisis mensual (últimos 12 meses)"
}
st.sidebar.info(info_periodo[periodo_seleccionado])

# Información de la máquina seleccionada
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Información del Centro de costos de energía")

info_maquinas = {
    "H75": {
        "Tipo": "Hidraúlica",
        "Fuerza de cierre": "120 Ton",
        "Potencia": "185 kW",
    },
    "Extrusora LEISTRITZ ZSE-27": {
        "Tipo": "Extrusión Doble Tornillo",
        "Diámetro": "27 mm",
        "Potencia": "225 kW", 
        "Material": "PVC, PP, Compounds",
        "Estado": "🟢 Operativa"
    },
    "Inyectora ENGEL e-motion 310": {
        "Tipo": "Inyección Eléctrica",
        "Capacidad": "310 gr",
        "Potencia": "160 kW",
        "Material": "PET, PA, PC",
        "Estado": "🟡 Mantenimiento"
    }
}

info = info_maquinas[maquina_seleccionada]
for key, value in info.items():
    st.sidebar.write(f"**{key}:** {value}")

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"⚡ CUSUM - {maquina_seleccionada} ({periodo_seleccionado})")
    
    # Generar y mostrar gráfico
    numero_periodos = {
        "Día": 30,      # 30 días
        "Semana": 24,   # 24 semanas
        "Mes": 12       # 12 meses
    }
    
    tiempo, frente_a_abt, frente_a_linea_base = generar_datos_energia(
        maquina_seleccionada, 
        periodo_seleccionado, 
        numero_periodos[periodo_seleccionado]
    )
    
    # Crear DataFrame para el gráfico
    etiqueta_tiempo = {
        "Día": "Día",
        "Semana": "Semana",
        "Mes": "Mes"
    }
    
    df_grafico = pd.DataFrame({
        etiqueta_tiempo[periodo_seleccionado]: tiempo,
        'Frente a ABT': frente_a_abt,
        'Frente a Linea Base': frente_a_linea_base
    })
    
    # Mostrar gráfico de líneas
    st.line_chart(df_grafico.set_index(etiqueta_tiempo[periodo_seleccionado]))
    
    # Mostrar estadísticas
    st.subheader("📊 Métricas de Control")
    mostrar_estadisticas(maquina_seleccionada, periodo_seleccionado)
    
    # Tabla de datos
    with st.expander("📋 Ver Datos Detallados"):
        st.dataframe(df_grafico, use_container_width=True)

with col2:
    st.subheader("🤖 ¡Hola! Soy tú asistente S.O.S EnergIA")
    
    # Inicializar el historial de chat
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
        # Mensaje de bienvenida
        st.session_state.mensajes.append({
            "role": "assistant", 
            "content": "¿En que puedo ayudarte desde nuestro centro de analítica de datos para el Sistema de Gestión Energética?"
        })
    
    # Preguntas sugeridas (solo mostrar si no hay muchos mensajes)
    if len(st.session_state.mensajes) <= 2:
        st.markdown("**💡 Preguntas sugeridas:**")
        
        # Inicializar pregunta seleccionada si no existe
        if "pregunta_seleccionada" not in st.session_state:
            st.session_state.pregunta_seleccionada = ""
        
        if st.button("⚡ ¿Cuál es el consumo actual?", use_container_width=True):
            st.session_state.pregunta_seleccionada = "¿Cuál es el consumo energético actual de esta máquina?"
        
        if st.button("📊 ¿Cómo está la eficiencia?", use_container_width=True):
            st.session_state.pregunta_seleccionada = "¿Cómo está la eficiencia energética de esta máquina?"
            
        if st.button("🔧 ¿Cuál es el estado actual?", use_container_width=True):
            st.session_state.pregunta_seleccionada = "¿Cuál es el estado actual de la máquina?"
        
        st.markdown("---")
    
    # Mostrar historial de mensajes
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])
    
    # Campo de entrada de texto con pregunta precargada
    prompt_default = st.session_state.get("pregunta_seleccionada", "")
    if prompt_default:
        # Mostrar la pregunta seleccionada en un input editable
        prompt = st.text_input("Escribe tú pregunta:", value=prompt_default, key="input_prompt")
        if st.button("📤 Enviar pregunta", use_container_width=True):
            if prompt.strip():
                # Limpiar la pregunta seleccionada después de enviar
                st.session_state.pregunta_seleccionada = ""
                # Procesar la pregunta
                st.session_state.mensajes.append({"role": "user", "content": prompt})
                st.rerun()
    else:
        prompt = st.chat_input("Consulta sobre las máquinas...")
    
    # Botón limpiar chat en la columna del bot
    if st.button("🗑️ Limpiar Chat", use_container_width=True):
        st.session_state.mensajes = [{
            "role": "assistant", 
            "content": "Chat reiniciado. ¿En qué puedo ayudarte?"
        }]
        if "pregunta_seleccionada" in st.session_state:
            st.session_state.pregunta_seleccionada = ""
        st.rerun()
    
    # Procesar prompt si existe
    if prompt and prompt.strip():
        # Agregar mensaje del usuario al historial
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta del asistente
        with st.chat_message("assistant"):
            numero_periodos = {
                "Día": 30,
                "Semana": 24,
                "Mes": 12
            }
            
            tiempo, frente_a_abt, frente_a_linea_base = generar_datos_energia(
                maquina_seleccionada, 
                periodo_seleccionado, 
                numero_periodos[periodo_seleccionado]
            )
            
            # Unidades según el periodo
            unidad_periodo = {
                "Día": "kWh/día",
                "Semana": "kWh/semana",
                "Mes": "kWh/mes"
            }
            unidad = unidad_periodo[periodo_seleccionado]
            
            # Respuestas basadas en palabras clave
            if "consumo" in prompt.lower():
                respuesta = f"La {maquina_seleccionada} tiene un consumo teórico promedio de {np.mean(frente_a_abt):.1f} {unidad} y real de {np.mean(frente_a_linea_base):.1f} {unidad} (análisis {periodo_seleccionado.lower()})."
            elif "eficiencia" in prompt.lower():
                diferencia = np.mean(frente_a_linea_base) - np.mean(frente_a_abt)
                eficiencia = (1 - abs(diferencia)/np.mean(frente_a_abt)) * 100
                respuesta = f"La eficiencia energética {periodo_seleccionado.lower()} es del {eficiencia:.1f}%. {'🟢 Excelente rendimiento.' if eficiencia > 90 else '🟡 Se recomienda revisión.'}"
            elif "máximo" in prompt.lower() or "pico" in prompt.lower():
                respuesta = f"Pico máximo ({periodo_seleccionado.lower()}): Teórico {np.max(frente_a_abt):.1f} {unidad}, Real {np.max(frente_a_linea_base):.1f} {unidad}."
            elif "mínimo" in prompt.lower():
                respuesta = f"Consumo mínimo ({periodo_seleccionado.lower()}): Teórico {np.min(frente_a_abt):.1f} {unidad}, Real {np.min(frente_a_linea_base):.1f} {unidad}."
            elif "periodo" in prompt.lower():
                respuesta = f"Actualmente estás visualizando datos por {periodo_seleccionado.lower()}. Puedes cambiar el periodo en el panel de control del sidebar."
            elif "material" in prompt.lower():
                materiales = {
                    "H75": "PP, PE, ABS", 
                    "Extrusora LEISTRITZ ZSE-27": "PVC, PP, Compounds", 
                    "Inyectora ENGEL e-motion 310": "PET, PA, PC"
                }
                respuesta = f"Materiales procesados: {materiales.get(maquina_seleccionada, 'N/A')}"
            elif "estado" in prompt.lower() or "mantenimiento" in prompt.lower():
                estados = {
                    "H75": "🟢 Operativa - Funcionamiento normal", 
                    "Extrusora LEISTRITZ ZSE-27": "🟢 Operativa - Funcionamiento normal", 
                    "Inyectora ENGEL e-motion 310": "🟡 En mantenimiento preventivo"
                }
                respuesta = f"Estado actual: {estados.get(maquina_seleccionada, 'N/A')}"
            else:
                respuesta = f"Analizando {maquina_seleccionada} por {periodo_seleccionado.lower()}. Puedes preguntar sobre: consumo, eficiencia, picos, periodo, materiales, estado o mantenimiento."
            
            st.markdown(respuesta)
        
        # Agregar respuesta al historial
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})

# Botón de control en el sidebar
if st.sidebar.button("🔄 Actualizar Datos", use_container_width=True):
    st.rerun()

# Métricas de Diagnóstico
st.markdown("---")
st.subheader("📈 Métricas de Diagnóstico")

col_res1, col_res2, col_res3 = st.columns(3)

# Calcular métricas globales
todas_maquinas = []
numero_periodos_calc = {
    "Día": 30,
    "Semana": 24,
    "Mes": 12
}

for maquina in maquinas:
    _, teorico, real = generar_datos_energia(
        maquina, 
        periodo_seleccionado, 
        numero_periodos_calc[periodo_seleccionado]
    )
    todas_maquinas.append({
        'maquina': maquina,
        'teorico': np.mean(teorico),
        'real': np.mean(real),
        'eficiencia': (1 - abs(np.mean(real) - np.mean(teorico))/np.mean(teorico)) * 100
    })

with col_res1:
    Ton=1200
    total_teorico = sum([m['teorico'] for m in todas_maquinas])
    total_real = sum([m['real'] for m in todas_maquinas])
    st.metric("Lote por Molde", f"{Ton:.0f} kg", f"{total_real - total_teorico:.0f} vs teórico")

with col_res2:
    Lr=560
    eficiencia_promedio = np.mean([m['eficiencia'] for m in todas_maquinas])
    st.metric("Lote por referencia", f"{Lr:.0f} kg")

with col_res3:
    fpm=18
    st.metric("Flujo por Molde", f"{fpm:.0f} kg/h")

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray; font-size: 14px;'>
    🏭 ESTRA - Sistema de Análisis de Centros de Costos de Energía | Análisis por {periodo_seleccionado} | Powered by SUME--SOSPOL
    </div>
    """, 
    unsafe_allow_html=True
)
