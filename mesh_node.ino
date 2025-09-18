/*
  ESP-NOW Mesh Prototype for ESP32 (Arduino)
  - Each node broadcasts MeshPacket frames
  - Simple multi-hop forwarding based on TTL and seen-sequence filtering
  - Basic XOR obfuscation with a pre-shared key (educational only)

  Configure NODE_ID and IS_GATEWAY before flashing.
*/

#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>

// -------- CONFIG --------
// Unique node ID (1..254)
#ifndef NODE_ID
#define NODE_ID 1
#endif

// If true, this node will act as a gateway and print to Serial
#ifndef IS_GATEWAY
#define IS_GATEWAY false
#endif

// Pre-shared key for XOR obfuscation (example: 16 bytes). Change per network.
const uint8_t PSK[] = { 0x42,0x37,0xAA,0x55,0x11,0x22,0x33,0x44,0x99,0x88,0x77,0x66,0xFE,0xDC,0xBA,0x10 };
const size_t PSK_LEN = sizeof(PSK);

// Mesh parameters
const uint8_t MAX_TTL = 5;

// Packet structure
typedef struct __attribute__((packed)) {
  uint8_t src;
  uint8_t dst;
  uint8_t ttl;
  uint16_t seq;
  uint8_t payload_len;
  // payload follows
} MeshPacketHeader;

// Simple seen-sequence table (for duplicate suppression)
#define SEEN_TABLE_SIZE 64
struct SeenEntry { uint8_t src; uint16_t seq; unsigned long t; };
SeenEntry seen_table[SEEN_TABLE_SIZE];

// sequence counter
uint16_t tx_seq = 0;

// callback for sent status
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  // optional: could log
}

// callback for receiving data
void OnDataRecv(const uint8_t *mac, const uint8_t *incomingData, int len) {
  if (len < (int)sizeof(MeshPacketHeader)) return;
  MeshPacketHeader hdr;
  memcpy(&hdr, incomingData, sizeof(MeshPacketHeader));
  uint8_t payload_len = hdr.payload_len;
  if (payload_len > 240) return; // safety
  const uint8_t *enc_payload = incomingData + sizeof(MeshPacketHeader);

  // decode payload (XOR with PSK)
  uint8_t payload[241];
  for (int i=0;i<payload_len;i++) payload[i] = enc_payload[i] ^ PSK[i % PSK_LEN];

  // duplicate suppression (simple)
  bool seen = false;
  for (int i=0;i<SEEN_TABLE_SIZE;i++) {
    if (seen_table[i].src == hdr.src && seen_table[i].seq == hdr.seq) { seen = true; break; }
  }
  if (seen) return;
  int idx = (hdr.src + hdr.seq) % SEEN_TABLE_SIZE;
  seen_table[idx].src = hdr.src;
  seen_table[idx].seq = hdr.seq;
  seen_table[idx].t = millis();

  // Deliver locally if dest matches or broadcast (0xFF)
  if (hdr.dst == NODE_ID || hdr.dst == 0xFF) {
    if (IS_GATEWAY) {
      Serial.printf("[DELIVER] from %u seq %u ttl %u len %u: ", hdr.src, hdr.seq, hdr.ttl, payload_len);
      for (int i=0;i<payload_len;i++) Serial.write(payload[i]);
      Serial.println();
    }
  }

  // Forward if not for me and ttl > 0
  if (hdr.dst != NODE_ID && hdr.ttl > 0) {
    MeshPacketHeader fwd = hdr;
    fwd.ttl = hdr.ttl - 1;
    uint8_t buf[300];
    memcpy(buf, &fwd, sizeof(MeshPacketHeader));
    for (int i=0;i<payload_len;i++) buf[sizeof(MeshPacketHeader)+i] = payload[i] ^ PSK[i % PSK_LEN];
    esp_err_t res = esp_now_send(nullptr, buf, sizeof(MeshPacketHeader) + payload_len);
    if (IS_GATEWAY) Serial.printf("[FWD] from %u -> %u seq %u newttl %u\n", hdr.src, hdr.dst, hdr.seq, fwd.ttl);
  }
}

// helper to create and send a message
void send_message(uint8_t dst, const uint8_t *data, uint8_t len) {
  if (len > 240) len = 240;
  tx_seq++;
  uint8_t buf[300];
  MeshPacketHeader hdr;
  hdr.src = NODE_ID;
  hdr.dst = dst;
  hdr.ttl = MAX_TTL;
  hdr.seq = tx_seq;
  hdr.payload_len = len;
  memcpy(buf, &hdr, sizeof(MeshPacketHeader));
  for (int i=0;i<len;i++) buf[sizeof(MeshPacketHeader) + i] = data[i] ^ PSK[i % PSK_LEN];
  esp_err_t res = esp_now_send(nullptr, buf, sizeof(MeshPacketHeader) + len);
  if (IS_GATEWAY) Serial.printf("[SENT] to %u seq %u len %u\n", dst, tx_seq, len);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  esp_now_register_send_cb(OnDataSent);
  esp_now_register_recv_cb(OnDataRecv);
  Serial.printf("Node %u started. Gateway=%s\n", NODE_ID, IS_GATEWAY? "YES":"NO");
  if (IS_GATEWAY) Serial.println("Type: send <dst> <text>  e.g. send 3 Hello");
}

void loop() {
  // On gateway, allow typing send commands via Serial
  if (IS_GATEWAY && Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.startsWith("send ")) {
      int sp1 = line.indexOf(' ');
      int sp2 = line.indexOf(' ', sp1+1);
      if (sp2 > sp1) {
        String dsts = line.substring(sp1+1, sp2);
        uint8_t dst = dsts.toInt();
        String payload = line.substring(sp2+1);
        uint8_t buf[241];
        payload.getBytes(buf, payload.length()+1);
        send_message(dst, buf, payload.length());
      }
    }
  }
  delay(10);
}