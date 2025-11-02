// WebSocket Client for Real-time Communication

export class ChatWebSocket {
  private ws: WebSocket | null = null;
  private clientId: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(clientId: string) {
    this.clientId = clientId;
  }

  connect(onMessage: (data: any) => void, onError?: (error: any) => void) {
    const wsUrl = `ws://localhost:8000/ws/chat/${this.clientId}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(onMessage, onError);
    };
  }

  sendMessage(content: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'message',
        content,
        timestamp: new Date().toISOString()
      }));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private attemptReconnect(onMessage: (data: any) => void, onError?: (error: any) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(onMessage, onError);
      }, 2000 * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }
}
