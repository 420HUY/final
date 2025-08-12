```mermaid
flowchart LR
  A0["Am thanh dau vao<br/>(WAV/MP3)"]:::blue --> M1

  subgraph M1[Module 1 - Phan biet nguoi noi & Cat doan]
    direction TB
    L1["Tai audio + mau giong da biet"]:::blue
    D1["Phan biet nguoi noi<br/>pyannote/speaker-diarization-3.1"]:::blue
    E1["Embedding giong noi<br/>pyannote/embedding + cosine"]:::blue
    S1["Phat hien im lang (pydub)<br/>-> vung tieng noi"]:::blue
    C1["Cat doan theo speaker/time"]:::blue
    L1 --> D1 --> E1 --> S1 --> C1
  end

  C1 --> F1[Thu muc Audio Segments]
  F1 --> M2

  subgraph M2[Module 2 - Nhan dang tieng noi (PhoWhisper)]
    direction TB
    P2["Tien xu ly:<br/>Resample 16kHz, mono<br/>Chuan hoa bien do"]:::yellow
    F2["Trich dac trung:<br/>log-Mel spectrograms"]:::yellow
    A2["ASR Model:<br/>vinai/PhoWhisper-large (FP16)<br/>chunk_length 20s, batch 2"]:::yellow
    O2["Hau xu ly:<br/>Ghep doan; gan speaker + thoi gian<br/>Cham cau, viet hoa; Luu transcript.txt"]:::yellow
    P2 --> F2 --> A2 --> O2
  end

  O2 --> T1[Transcript (.txt)]
  O2 --> DB

  subgraph M3[Module 3 - Luu tru/Xu ly du lieu]
    direction TB
    DB[(Firebase / CSDL)]:::red
  end

  DB --> SRCH

  subgraph M4[Module 4 - Tim kiem]
    direction TB
    SRCH[Search tren transcript]:::green
  end

  N1["Smart cleanup:<br/>torch.cuda.empty_cache()<br/>gc.collect()<br/>Chay theo chu ky (samples/segments/batches)"]
  N1 --- A2

  classDef blue fill:#cfe8ff,stroke:#5aa0ff,stroke-width:1px,color:#003b73;
  classDef yellow fill:#ffe89c,stroke:#f6b100,stroke-width:1px,color:#4a3b00;
  classDef red fill:#ffd3d3,stroke:#ff6b6b,stroke-width:1px,color:#6b0000;
  classDef green fill:#d7f9e9,stroke:#2ecc71,stroke-width:1px,color:#0d6f43;
```