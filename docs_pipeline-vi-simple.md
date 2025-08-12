```mermaid
flowchart LR
  A0["Âm thanh đầu vào<br/>(WAV/MP3)"] --> M1

  subgraph M1[Module 1 - Phân biệt người nói & Cắt đoạn]
    direction TB
    L1["Tải audio + mẫu giọng đã biết"]
    D1["Diarization<br/>pyannote/speaker-diarization-3.1"]
    E1["Embedding giọng nói<br/>pyannote/embedding + cosine"]
    S1["Phát hiện im lặng (pydub)<br/>→ vùng tiếng nói"]
    C1["Cắt đoạn theo speaker/time"]
    L1 --> D1 --> E1 --> S1 --> C1
  end

  C1 --> F1[Thư mục Audio Segments]
  F1 --> M2

  subgraph M2[Module 2 - ASR (PhoWhisper)]
    direction TB
    P2["Tiền xử lý:<br/>Resample 16kHz, mono<br/>Chuẩn hoá"]
    F2["Trích đặc trưng:<br/>log-Mel"]
    A2["ASR Model:<br/>vinai/PhoWhisper-large (FP16)<br/>chunk 20s, batch 2"]
    O2["Hậu xử lý:<br/>Ghép đoạn + speaker + time<br/>Chấm câu, viết hoa<br/>Lưu transcript.txt"]
    P2 --> F2 --> A2 --> O2
  end

  O2 --> T1[Transcript (.txt)]

  subgraph M3[Module 3 - Lưu trữ/Xử lý dữ liệu]
    direction TB
    DB[(Firebase / CSDL)]
  end

  O2 --> DB

  subgraph M4[Module 4 - Tìm kiếm]
    SRCH[Search]
  end

  DB --> SRCH

  N1["Smart cleanup:<br/>torch.cuda.empty_cache()<br/>gc.collect()<br/>Chu kỳ theo samples/segments/batches"]
  N1 --- A2
```