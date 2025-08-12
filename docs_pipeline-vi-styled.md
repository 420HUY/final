```mermaid
flowchart LR
  A0["Âm thanh đầu vào<br/>(WAV/MP3)"] --> M1

  subgraph M1[Module 1 — Phân biệt người nói & Cắt đoạn]
    direction TB
    L1["Tải audio + mẫu giọng đã biết"]
    D1["Phân biệt người nói<br/>pyannote/speaker-diarization-3.1"]
    E1["Embedding giọng nói<br/>pyannote/embedding + cosine"]
    S1["Phát hiện im lặng (pydub)<br/>→ vùng tiếng nói"]
    C1["Cắt đoạn theo speaker/time"]
    L1 --> D1 --> E1 --> S1 --> C1
  end

  C1 --> F1[Thư mục Audio Segments]
  F1 --> M2

  subgraph M2[Module 2 — Nhận dạng tiếng nói (PhoWhisper)]
    direction TB
    P2["Tiền xử lý:<br/>Resample 16kHz, mono<br/>Chuẩn hoá biên độ"]
    F2["Trích đặc trưng:<br/>log-Mel spectrograms"]
    A2["ASR Model:<br/>vinai/PhoWhisper-large (FP16)<br/>chunk_length 20s, batch 2"]
    O2["Hậu xử lý:<br/>Ghép đoạn; gắn speaker + thời gian<br/>Chấm câu, viết hoa; Lưu transcript.txt"]
    P2 --> F2 --> A2 --> O2
  end

  O2 --> T1[Transcript (.txt)]
  O2 --> DB

  subgraph M3[Module 3 — Lưu trữ/Xử lý dữ liệu]
    direction TB
    DB[(Firebase / CSDL)]
  end

  DB --> SRCH

  subgraph M4[Module 4 — Tìm kiếm]
    SRCH[Search trên transcript]
  end

  N1["Smart cleanup:<br/>torch.cuda.empty_cache()<br/>gc.collect()<br/>Chạy theo chu kỳ (samples/segments/batches)"]
  N1 --- A2

  classDef blue fill:#cfe8ff,stroke:#5aa0ff,stroke-width:1px,color:#003b73;
  classDef yellow fill:#ffe89c,stroke:#f6b100,stroke-width:1px,color:#4a3b00;
  classDef red fill:#ffd3d3,stroke:#ff6b6b,stroke-width:1px,color:#6b0000;
  classDef green fill:#d7f9e9,stroke:#2ecc71,stroke-width:1px,color:#0d6f43;

  class A0 blue;
  class L1,D1,E1,S1,C1 blue;
  class P2,F2,A2,O2 yellow;
  class DB red;
  class SRCH green;
```