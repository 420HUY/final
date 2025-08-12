```mermaid
flowchart LR
  A0[Âm thanh đầu vào\n(WAV/MP3)]:::icon --> M1

  subgraph M1[Module 1 — Phân biệt người nói & Cắt đoạn]
    direction TB
    L1[Tải audio + các mẫu giọng đã biết]:::blue
    D1[Phân biệt người nói\npyannote/speaker-diarization-3.1]:::blue
    E1[Embedding giọng nói\npyannote/embedding\n+ so khớp cosine với mẫu]:::blue
    S1[Phát hiện im lặng (pydub)\n→ vùng có tiếng nói]:::blue
    C1[Cắt đoạn theo speaker/thời gian]:::blue
    L1 --> D1 --> E1 --> S1 --> C1
  end

  C1 --> F1[Thư mục Audio Segments]:::folder
  F1 --> M2

  subgraph M2[Module 2 — Nhận dạng tiếng nói (PhoWhisper)]
    direction TB
    P2[Tiền xử lý:\n- Resample 16kHz, mono\n- Chuẩn hoá biên độ]:::yellow
    F2[Trích đặc trưng:\nlog-Mel spectrograms]:::yellow
    A2[Mô hình ASR:\nvinai/PhoWhisper-large (FP16)\nchunk_length=20s, batch=2]:::yellow
    O2[Hậu xử lý:\n- Ghép đoạn\n- Gắn nhãn speaker + timestamps\n- Chấm câu, viết hoa\n- Lưu transcript.txt]:::yellow
    P2 --> F2 --> A2 --> O2
  end

  O2 --> T1[Transcript (.txt)]:::folder
  O2 --> M3

  subgraph M3[Module 3 — Lưu trữ/Xử lý dữ liệu]
    direction TB
    DB[(Firebase / CSDL)]:::red
  end

  O2 --> DB
  DB --> M4

  subgraph M4[Module 4 — Tìm kiếm]
    SRCH[Tìm kiếm trên transcript đã lưu]:::green
  end

  note1:::note --- A2
  note1[Smart cleanup:\n- torch.cuda.empty_cache()\n- gc.collect()\n- Chạy theo chu kỳ: sau N samples/segments/batches]

classDef blue fill:#cfe8ff,stroke:#5aa0ff,stroke-width:1px,color:#003b73;
classDef yellow fill:#ffe89c,stroke:#f6b100,stroke-width:1px,color:#4a3b00;
classDef red fill:#ffd3d3,stroke:#ff6b6b,stroke-width:1px,color:#6b0000;
classDef green fill:#d7f9e9,stroke:#2ecc71,stroke-width:1px,color:#0d6f43;
classDef folder fill:#fff,stroke:#999,stroke-dasharray:3 3,color:#333;
classDef icon fill:#e6f0ff,stroke:#5aa0ff;
classDef note fill:#f3f4f6,stroke:#9ca3af,stroke-dasharray:4 4,color:#111827;
```