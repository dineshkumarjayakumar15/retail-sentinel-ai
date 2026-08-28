type WebSocketCallback = (data: any) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private listeners: Set<WebSocketCallback> = new Set();
  private reconnectInterval: number = 3000;
  private isConnected: boolean = false;

  public connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        console.log('[WebSocket] Connected to Retail Sentinel AI dashboard stream');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.listeners.forEach((listener) => listener(data));
        } catch (e) {
          console.error('[WebSocket] Failed to parse message:', e);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        console.log('[WebSocket] Disconnected. Reconnecting in 3s...');
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.ws.onerror = (err) => {
        console.warn('[WebSocket] Connection error:', err);
        this.ws?.close();
      };
    } catch (e) {
      console.warn('[WebSocket] Error setting up connection:', e);
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  public subscribe(callback: WebSocketCallback) {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  }

  public getStatus(): boolean {
    return this.isConnected;
  }
}

export const wsClient = new WebSocketClient();
