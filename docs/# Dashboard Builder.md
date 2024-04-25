::: mermaid

sequenceDiagram
    participant User as Usuario
    participant Frontend
    participant Backend
    participant AutoGen_Proxy as AutoGen Studio de Microsoft
    participant DB as Base de datos PostgreSQL
    participant Proxy_Query as Agente de Consulta SQL
    participant Proxy_DT as Agente de DataTables
    participant Proxy_HC as Agente de Highcharts

    User->>Frontend: Envia mensaje
    Frontend->>Backend: Envía mensaje (WebSocket)
    Backend->>AutoGen_Proxy: Envía texto
    AutoGen_Proxy-->>AutoGen_Proxy: Identifica Intención
    alt Crear nueva consulta
        AutoGen_Proxy->>Proxy_Query: Solicita consulta SQL
        Proxy_Query->>DB: Ejecuta consulta SQL
        DB-->>Proxy_Query: Resultados en datos
        Proxy_Query-->>Backend: Datos para visualización
        Backend->>Proxy_DT: Solicita generación de código para DataTables
        Proxy_DT-->>Backend: Código para DataTables
        Backend->>Proxy_HC: Solicita generación de código para Highcharts
        Proxy_HC-->>Backend: Código para Highcharts
    else Modificar consulta
        AutoGen_Proxy->>Proxy_Query: Crea y ejecuta nueva consulta SQL
        Proxy_Query->>DB: Ejecuta consulta
        DB-->>Proxy_Query: Resultados actualizados
        Proxy_Query-->>Backend: Datos actualizados
        opt Modificar código DataTables
            Backend->>Proxy_DT: Actualiza código DataTables
            Proxy_DT-->>Backend: Código DataTables actualizado
        end
        opt Modificar código Highcharts
            Backend->>Proxy_HC: Actualiza código Highcharts
            Proxy_HC-->>Backend: Código Highcharts actualizado
        end
    end
    Backend->>Frontend: Envía código (WebSocket)
    Frontend->>User: Renderiza DataTables y Highcharts
    note right of Frontend: DataTables y Highcharts
    Frontend-->>Frontend: Actualización dinámica
    Frontend-->>Frontend: Redibuja gráfica (Highcharts)
:::