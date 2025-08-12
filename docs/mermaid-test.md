# Mermaid Test File

This file contains simple Mermaid diagrams to test GitHub compatibility.

## Simple Flow Test

```mermaid
graph LR
    A[Input] --> B[Process]
    B --> C[Output]
```

## Test with Line Breaks

```mermaid
graph LR
    A[Audio<br/>File] --> B[Processing<br/>Module]
    B --> C[Text<br/>Output]
```

## Test with Multiple Modules

```mermaid
graph LR
    A[Start] --> M1[Module 1<br/>Diarization]
    M1 --> M2[Module 2<br/>ASR]
    M2 --> M3[Module 3<br/>Storage]
    M3 --> M4[Module 4<br/>Search]
    M4 --> E[End]
```

## Test with Colors

```mermaid
graph LR
    A[Input] --> B[Process]
    B --> C[Output]
    
    classDef input fill:#e1f5fe,stroke:#01579b
    classDef process fill:#e8f5e8,stroke:#1b5e20
    classDef output fill:#fff3e0,stroke:#e65100
    
    class A input
    class B process
    class C output
```

This test file ensures that:
- Basic Mermaid syntax works
- Line breaks with `<br/>` work correctly
- Multiple connected nodes work
- CSS classes and colors work
- No `direction TB` is used in subgraphs