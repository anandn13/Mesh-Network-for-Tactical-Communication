# Mesh Network Architecture

## Node Roles
- **Gateway**: Serial bridge to PC (dashboard/logger)
- **Relay Node**: Forwards packets
- **End Node**: Sends/receives only

## Packet Format
- src_id (1B)
- dst_id (1B) — `255` for broadcast
- ttl (1B)
- seq (2B)
- payload_len (1B)
- payload (N)

## Fault Tolerance
- Nodes rebroadcast packets if TTL > 0
- Seen-table prevents duplicates
- If one node goes down, others reroute

## Monitoring
- Gateway prints serial logs
- Dashboard shows packets in real-time
- Logger saves structured CSV