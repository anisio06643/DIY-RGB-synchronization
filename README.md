<img width="797" height="372" alt="image" src="https://github.com/user-attachments/assets/415237d1-c26f-4cf6-9f3d-9e7dfd480034" />



# DIY Ultra-Fast 60FPS Ambilight System

A high-performance, real-time screen reactive ambient lighting system using Python, OpenCV, and an ESP32. 

Unlike traditional DIY Ambilight setups that pass slow, comma-separated text strings over serial (which lag heavily at higher frame rates), this system utilizes a **raw binary payload stream** prefixed with a 3-byte validation header (`'M'`, `'G'`, `'K'`). This enables a rock-solid, zero-latency **60 FPS** refresh rate for smooth gaming and media consumption.

---

## 🚀 Features

* **Ultra-low Latency:** Direct memory frame grabbing via `mss` and binary serialization.
* **Intelligent Saturation Boosting:** Dynamically intensifies vibrant colors while ignoring neutral tones.
* **Smart White Passthrough:** Detects whites and pastels to prevent unnatural color shifts.
* **Temporal Smoothing:** Linear interpolation (LERP) prevents rapid LED flickering.
* **Fault-Tolerant Protocol:** ESP32 drops malformed data frames automatically using an explicit magic byte header.

---

## 🔌 Hardware & Wiring

### Components Required
1. **ESP32 Development Board** (NodeMCU or similar micro-controller)
2. **WS2812B LED Strip** (5V Addressable RGB)
3. **5V External Power Supply** (Amperage depends on LED count; roughly 60mA per LED at full white brightness)
4. **330Ω Resistor** (Optional but highly recommended for the data line)

### Wiring Diagram

> ⚠️ **CRITICAL:** Always connect the **GND** of the external 5V power supply to the **GND** of the ESP32. If you skip this, the data signal will experience massive interference, causing your LEDs to flicker wildly. Never attempt to power a long LED strip directly from the ESP32's 5V pin.

