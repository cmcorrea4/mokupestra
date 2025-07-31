import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="ESTRA - Monitoreo Energético",
    page_icon="🏭",
    layout="wide"
)

# Título principal
st.title("🏭 ESTRA - Plataforma inteligente de Analítica en consumo de Energía")

# Función para generar datos sintéticos
def generar_datos_energia(centro, semanas=24):
    """Genera datos sintéticos para cada centro de costos"""
    tiempo = np.arange(1, semanas + 1)
    
    # Parámetros base para cada máquina
    parametros = {
        "Inyectora HAITIAN MA-1200": {
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
    
    # Generar curvas simétricas
    consumo_teorico = params["base"] + params["amplitud1"] * np.sin(2 * np.pi * tiempo / semanas + params["fase1"])
    consumo_real = params["base"] - params["amplitud2"] * np.sin(2 * np.pi * tiempo / semanas + params["fase2"])
    
    # Asegurar que empiecen y terminen en el mismo punto
    consumo_teorico[0] = consumo_teorico[-1] = params["base"]
    consumo_real[0] = consumo_real[-1] = params["base"]
    
    return tiempo, consumo_teorico, consumo_real

# Función para mostrar estadísticas
def mostrar_estadisticas(centro_seleccionado):
    """Muestra estadísticas del centro seleccionado"""
    tiempo, consumo_teorico, consumo_real = generar_datos_energia(centro_seleccionado)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="CUSUM  Esperado",
            value=f"{np.mean(consumo_teorico):.1f} kWh",
            delta=f"±{np.std(consumo_teorico):.1f}"
        )
    
    with col2:
        st.metric(
            label="CUSUM Alcanzado", 
            value=f"{np.mean(consumo_real):.1f} kWh",
            delta=f"±{np.std(consumo_real):.1f}"
        )
    
    with col3:
        diferencia = np.mean(consumo_real) - np.mean(consumo_teorico)
        st.metric(
            label="Desviación Energética",
            value=f"{diferencia:.1f} kWh",
            delta=f"{(diferencia/np.mean(consumo_teorico)*100):.1f}%"
        )
    
    with col4:
        eficiencia = (1 - abs(diferencia)/np.mean(consumo_teorico)) * 100
        st.metric(
            label="Eficiencia Energética",
            value=f"{eficiencia:.1f}%",
            delta="✅ Óptima" if eficiencia > 90 else "⚠️ Revisar"
        )

# Sidebar para controles
st.sidebar.header("🔧 Panel de Control")

# Selectbox para máquinas
maquinas = [
    "Inyectora HAITIAN MA-1200",
    "Extrusora LEISTRITZ ZSE-27", 
    "Inyectora ENGEL e-motion 310"
]

maquina_seleccionada = st.sidebar.selectbox(
    "Selecciona la Máquina:",
    maquinas,
    index=0
)

# Información de la máquina seleccionada
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Información de Máquina")

info_maquinas = {
    "Inyectora HAITIAN MA-1200": {
        "Tipo": "Inyección por Tornillo",
        "Capacidad": "1,200 gr",
        "Potencia": "185 kW",
        "Material": "PP, PE, ABS",
        "Estado": "🟢 Operativa"
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
    st.subheader(f"⚡ Análisis Energético - {maquina_seleccionada}")
    
    # Generar y mostrar gráfico
    tiempo, consumo_teorico, consumo_real = generar_datos_energia(maquina_seleccionada)
    
    # Crear DataFrame para el gráfico
    df_grafico = pd.DataFrame({
        'Semana': tiempo,
        'Consumo Teórico': cusum_esperado,
        'Consumo Real': consumo_alcanzado
    })
    
    # Mostrar gráfico de líneas
    st.line_chart(df_grafico.set_index('Semana'))
    
    # Mostrar estadísticas
    st.subheader("📊 Métricas de Rendimiento Energético")
    mostrar_estadisticas(maquina_seleccionada)
    
    # Tabla de datos
    with st.expander("📋 Ver Datos Detallados"):
        st.dataframe(df_grafico, use_container_width=True)

with col2:
    st.subheader("🤖 Asistente ESTRA")
    
    # Inicializar el historial de chat
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
        # Mensaje de bienvenida
        st.session_state.mensajes.append({
            "role": "assistant", 
            "content": "¡Hola! Soy tú asistente S.O.S EnergIA. ¿En qué puedo ayudarte respecto a análisis de Gestión energética?"
        })
    
    # Mostrar historial de mensajes
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])
    
    # Campo de entrada de texto
    if prompt := st.chat_input("Consulta sobre las máquinas..."):
        # Agregar mensaje del usuario al historial
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta del asistente
        with st.chat_message("assistant"):
            tiempo, consumo_teorico, consumo_real = generar_datos_energia(maquina_seleccionada)
            
            # Respuestas basadas en palabras clave
            if "consumo" in prompt.lower():
                respuesta = f"La {maquina_seleccionada} tiene un consumo teórico promedio de {np.mean(consumo_teorico):.1f} kWh y real de {np.mean(consumo_real):.1f} kWh por semana."
            elif "eficiencia" in prompt.lower():
                diferencia = np.mean(consumo_real) - np.mean(consumo_teorico)
                eficiencia = (1 - abs(diferencia)/np.mean(consumo_teorico)) * 100
                respuesta = f"La eficiencia energética es del {eficiencia:.1f}%. {'🟢 Excelente rendimiento.' if eficiencia > 90 else '🟡 Se recomienda revisión.'}"
            elif "máximo" in prompt.lower() or "pico" in prompt.lower():
                respuesta = f"Pico máximo: Teórico {np.max(consumo_teorico):.1f} kWh, Real {np.max(consumo_real):.1f} kWh."
            elif "mínimo" in prompt.lower():
                respuesta = f"Consumo mínimo: Teórico {np.min(consumo_teorico):.1f} kWh, Real {np.min(consumo_real):.1f} kWh."
            elif "material" in prompt.lower():
                materiales = {
                    "Inyectora HAITIAN MA-1200": "PP, PE, ABS", 
                    "Extrusora LEISTRITZ ZSE-27": "PVC, PP, Compounds", 
                    "Inyectora ENGEL e-motion 310": "PET, PA, PC"
                }
                respuesta = f"Materiales procesados: {materiales.get(maquina_seleccionada, 'N/A')}"
            elif "estado" in prompt.lower() or "mantenimiento" in prompt.lower():
                estados = {
                    "Inyectora HAITIAN MA-1200": "🟢 Operativa - Funcionamiento normal", 
                    "Extrusora LEISTRITZ ZSE-27": "🟢 Operativa - Funcionamiento normal", 
                    "Inyectora ENGEL e-motion 310": "🟡 En mantenimiento preventivo"
                }
                respuesta = f"Estado actual: {estados.get(maquina_seleccionada, 'N/A')}"
            else:
                respuesta = f"Analizando {maquina_seleccionada}. Puedes preguntar sobre: consumo, eficiencia, picos, materiales, estado o mantenimiento."
            
            st.markdown(respuesta)
        
        # Agregar respuesta al historial
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})

# Botones de control
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("🗑️ Limpiar Chat"):
        st.session_state.mensajes = [{
            "role": "assistant", 
            "content": "Chat reiniciado. ¿En qué puedo ayudarte?"
        }]
        st.rerun()

with col_btn2:
    if st.button("🔄 Actualizar Datos"):
        st.rerun()

# Resumen ejecutivo
st.markdown("---")
st.subheader("📈 Resumen Ejecutivo ESTRA")

col_res1, col_res2, col_res3 = st.columns(3)

# Calcular métricas globales
todas_maquinas = []
for maquina in maquinas:
    _, teorico, real = generar_datos_energia(maquina)
    todas_maquinas.append({
        'maquina': maquina,
        'teorico': np.mean(teorico),
        'real': np.mean(real),
        'eficiencia': (1 - abs(np.mean(real) - np.mean(teorico))/np.mean(teorico)) * 100
    })

with col_res1:
    total_teorico = sum([m['teorico'] for m in todas_maquinas])
    total_real = sum([m['real'] for m in todas_maquinas])
    st.metric("Consumo Total Semanal", f"{total_real:.0f} kWh", f"{total_real - total_teorico:.0f} vs teórico")

with col_res2:
    eficiencia_promedio = np.mean([m['eficiencia'] for m in todas_maquinas])
    st.metric("Eficiencia Promedio Planta", f"{eficiencia_promedio:.1f}%")

with col_res3:
    maquinas_optimas = sum([1 for m in todas_maquinas if m['eficiencia'] > 90])
    st.metric("Máquinas en Óptimo Estado", f"{maquinas_optimas}/{len(maquinas)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 14px;'>
    🏭 ESTRA - Sistema de Monitoreo Energético Industrial | Powered by Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)
