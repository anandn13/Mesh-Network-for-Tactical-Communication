# Mesh Network for Tactical Communication

## 🔹 Overview
This project implements a **resilient mesh communication system** using **ESP32 (ESP-NOW)** for tactical or emergency use. Each node can send, forward, and receive encrypted messages even if intermediate nodes fail. The system ensures reliable **peer-to-peer links** without Wi-Fi or Internet.

Includes:
- ESP32 firmware (C++) for mesh nodes
- Streamlit dashboard for live monitoring
- Python logger for structured CSV logging
- Example outputs and test cases

---

## 🚀 Features
- **ESP-NOW Mesh**: Lightweight peer-to-peer communication
- **Fault Tolerance**: Packets reroute if nodes drop
- **Encryption (PSK XOR)**: Payload obfuscation, upgradable to AES
- **Streamlit UI**: Real-time message view
- **Logger Utility**: Serial-to-CSV structured logging
- **Example Scenarios**: Sending, forwarding, duplicate detection

---

## 📂 Project Structure

```
mesh-comm/
│
├── firmware/ # ESP32 Arduino sketches
│   └── mesh_node/mesh_node.ino
│
├── dashboard/ # PC tools
│   ├── app.py # Streamlit dashboard
│   └── logger.py # Serial-to-CSV logger
│
├── docs/
│   ├── example_output.txt # Example logs & outputs
│   ├── TROUBLESHOOTING.md # Troubleshooting guide
│   └── architecture.md # Mesh design explanation
│
├── requirements.txt # Python dependencies
├── .gitignore
└── README.md
```

---

## ⚡ Getting Started

### 1. Hardware
- 2+ ESP32 boards
- Micro-USB cables
- (Optional) LoRa modules for long-range

### 2. Setup Firmware
- Open `firmware/mesh_node/mesh_node.ino` in Arduino IDE
- Select **ESP32 Dev Module**
- Flash to each ESP32 (change `NODE_ID` per device)

### 3. Python Environment
```bash
pip install -r requirements.txt
```

### 4. Run Dashboard
```bash
streamlit run dashboard/app.py
```

### 5. Run Logger
```bash
python dashboard/logger.py --port /dev/ttyUSB0 --baud 115200 --out log.csv
```

---

## 📝 Example Output

See [docs/example_output.txt](docs/example_output.txt)
for a full run sample.

---

## 📊 Applications

- Tactical communication in defense
- Disaster recovery & rescue teams
- IoT field deployment without Wi-Fi
- Robust military-grade messaging

---

## 🔒 Security Note

Current payload obfuscation is XOR with PSK. Upgrade to AES for production security.

---

## 🤝 Contributing

Pull requests are welcome! For big changes, please open an issue first.

---

## 📜 License

MIT License