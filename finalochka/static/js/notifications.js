function showNotification(message, category = 'info') {
    const container = document.getElementById('notifications-container');
    
    // Создаем новый элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification ${category} show`;
    notification.textContent = message;
  
    // Добавляем уведомление в контейнер
    container.appendChild(notification);
  
    // Удаляем уведомление через 4 секунды
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => container.removeChild(notification), 500);
    }, 4000);
  }
  
  // Пример автоматической загрузки уведомлений из Flask-сессии
  document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_notifications')
      .then((response) => response.json())
      .then((notifications) => {
        notifications.forEach((notif) => {
          showNotification(notif.message, notif.category);
        });
      })
      .catch((err) => console.error('Ошибка загрузки уведомлений:', err));
  });
  