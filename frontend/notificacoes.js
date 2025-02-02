  // Atualize a URL do EventSource para o endpoint correto
  const eventSource = new EventSource('http://localhost:8000/notifications');

  eventSource.onmessage = function(event) {
      const notificationsDiv = document.getElementById('notifications');
      const newNotification = document.createElement('p');
      newNotification.textContent = `Nova mensagem recebida: ${event.data}`;
      notificationsDiv.appendChild(newNotification);
  };

  eventSource.onerror = function(error) {
      console.error('Erro SSE:', error);
      eventSource.close();
  };