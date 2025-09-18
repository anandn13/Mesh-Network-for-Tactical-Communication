# Troubleshooting Mesh Network (ESP-NOW)

## Common Issues

### 1. ESP-NOW fails to initialize
- **Symptom:** Serial prints “Error initializing ESP-NOW”.
- **Fix:** Check that board is set to “ESP32 Dev Module” (or correct ESP32 variant). Confirm ESP32 Arduino core installed in IDE.

### 2. No messages received / no forwarding
- **Symptoms:** Only “Node X started” message shown, nothing else.
- **Fixes:**
  - Ensure all nodes are on the same **Wi-Fi channel** (default channel 1 in firmware).
  - All nodes must have **matching PSK** (payloads will be garbage if not).
  - Try rebooting all nodes after flashing.
  - Confirm power supply is stable and micro-USB cable is good.

### 3. Duplicate or flood of messages
- **Symptom:** Serial log shows same [DELIVER] / [FWD] repeatedly.
- **Fix:** Increase `SEEN_TABLE_SIZE` in firmware if your network is larger or has more message volume.

### 4. Serial port not found (dashboard/logger)
- **Symptom:** “Could not open port…” or dashboard hangs.
- **Fixes:**
  - Double-check port name (e.g. `/dev/ttyUSB0` on Linux, `COM3` on Windows).
  - Only one program can open serial port at a time (close Arduino Serial Monitor before using dashboard/logger).
  - Check baud rate matches (should be 115200).

### 5. Gateway node not logging
- **Symptom:** You see [SENT] but no [DELIVER] or [FWD].
- **Fixes:**
  - Ensure `#define IS_GATEWAY true` is set on at least one node.
  - Use unique `NODE_ID` for each device.

### 6. General Debugging
- Use [logger.py](../dashboard/logger.py) to save all serial output for inspection.
- Add `Serial.println()` debug lines in firmware.

## Resources

- [ESP-NOW documentation (Espressif)](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/network/esp_now.html)
- [Arduino ESP32 core](https://github.com/espressif/arduino-esp32)

---