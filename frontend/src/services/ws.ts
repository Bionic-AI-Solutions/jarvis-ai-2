/**
 * JARVIS AI — WebSocket client for real-time updates.
 *
 * Story 2.1: Real-Time Step Progress
 * - Connects to backend WS at /ws
 * - Subscribes to execution events
 * - Dispatches events to Zustand store
 */

export type WsMessageType =
  | 'plan_ready'
  | 'step_started'
  | 'step_complete'
  | 'workflow_complete'
  | 'error'
  | 'heartbeat';

export interface WsMessage {
  type: WsMessageType;
  execution_id?: string;
  [key: string]: unknown;
}

type WsHandler = (msg: WsMessage) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: Map<string, Set<WsHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(url: string = 'ws://127.0.0.1:9000/ws') {
    this.url = url;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('[WS] Connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data);
        this.dispatch(msg);
      } catch {
        console.warn('[WS] Failed to parse message:', event.data);
      }
    };

    this.ws.onclose = () => {
      console.log('[WS] Disconnected');
      this.scheduleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('[WS] Error:', err);
    };
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /** Subscribe to an execution's updates */
  subscribe(executionId: string): void {
    this.send({
      type: 'subscribe',
      execution_id: executionId,
    });
  }

  /** Register a handler for a specific message type */
  on(type: string, handler: WsHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.handlers.get(type)?.delete(handler);
    };
  }

  /** Register a handler for ALL messages */
  onAny(handler: WsHandler): () => void {
    return this.on('*', handler);
  }

  private send(data: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  private dispatch(msg: WsMessage): void {
    // Type-specific handlers
    const typeHandlers = this.handlers.get(msg.type);
    if (typeHandlers) {
      typeHandlers.forEach((h) => h(msg));
    }

    // Wildcard handlers
    const anyHandlers = this.handlers.get('*');
    if (anyHandlers) {
      anyHandlers.forEach((h) => h(msg));
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    this.reconnectAttempts++;

    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Singleton
export const wsClient = new WebSocketClient();
