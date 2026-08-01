# ⚡ Crypto Sniper Engine

Un motor asíncrono defensivo de alta frecuencia para la detección e identificación de brechas de arbitraje Spot entre **Binance** y **OKX** en tiempo real.

Designed with an **Event-Driven Architecture**, prioritizing resilience, zero memory leaks, and high-precision execution over high-frequency noise.

---

## 🛠️ Arquitectura y Principios de Diseño

1. **Sniper Approach (Quality over Quantity):**
   - El sistema ignora brechas micro-centémicas y evalúa únicamente oportunidades con **ganancia neta garantizada $\ge \$1.00\text{ USD}$** tras deducir comisiones Taker (0.1%).
   - Requiere un **colchón de volumen de $2\times$** en la punta del libro (*OrderBook Depth*) antes de marcar una señal válida.

2. **Resiliencia & Stale Data Protection:**
   - Monitoreo asíncrono en tiempo real vía **WebSockets (CCXT Pro)** con latencias de evaluación de ~50ms.
   - Filtro de frescura de datos: Descarta automáticamente cualquier evento con más de **500 ms** de antigüedad.

3. **Circuit Breaker (Stop on First Error):**
   - Ante la primera falla no controlada de red o de la API, el sistema aborta de inmediato la ejecución mediante `sys.exit(1)` y envía una alerta de emergencia a Telegram para evitar operaciones a ciegas.

---

## 📂 Estructura del Proyecto

```text
crypto-sniper-engine/
├── config.py              # Umbrales del sistema y carga de variables (.env)
├── main.py                # Bucle asíncrono principal de asyncio
├── requirements.txt       # Dependencias principales
├── src/
│   ├── streamer.py        # Clientes WebSocket asíncronos
│   ├── evaluator.py       # Motor matemático del filtro Sniper
│   ├── circuit_breaker.py # Parada de emergencia y pausa de seguridad
│   ├── telegram_bot.py    # Notificaciones y comandos remotos (/status, /pause, /reset)
│   └── executor.py        # Disparo paralelo atómico vía CCXT
├── tests/
│   └── test_evaluator.py  # Pruebas unitarias automáticas con Pytest
└── systemd/
    └── sniper.service     # Configuración para despliegue 24/7 en Linux VPS